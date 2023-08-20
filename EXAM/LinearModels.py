import numpy as np
from numpy import linalg as la
from scipy.stats import norm
from tabulate import tabulate


def estimate( 
        y: np.ndarray, x: np.ndarray, transform='', T:int=None, robust = False, _lambda:int = 0, sigma2_c:int = 0, sigma2_u:int = 0
    ) -> list:
    """Uses the provided estimator (mostly OLS for now, and therefore we do 
    not need to provide the estimator) to perform a regression of y on x, 
    and provides all other necessary statistics such as standard errors, 
    t-values etc.  

    Args:
        >> y (np.array): Dependent variable (Needs to have shape 2D shape)
        >> x (np.array): Independent variable (Needs to have shape 2D shape)
        >> transform (str, optional): Defaults to ''. If the data is 
        transformed in any way, the following transformations are allowed:
            '': No transformations
            'fd': First-difference
            'be': Between transformation
            'fe': Within transformation
            're': Random effects estimation.
        >>t (int, optional): If panel data, t is the number of time periods in
        the panel, and is used for estimating the variance. Defaults to None.

    Returns:
        list: Returns a dictionary with the following variables:
        'b_hat', 'se', 'sigma2', 't_values', 'R2', 'cov'
    """

    assert y.ndim == 2
    assert x.ndim == 2 
    assert y.shape[1] == 1
    
    b_hat = est_ols(y, x)  # Estimated coefficients
    residual = y - x@b_hat  # Calculated residuals
    SSR = residual.T@residual  # Sum of squared residuals
    SST = (y - np.mean(y)).T@(y - np.mean(y))  # Total sum of squares
    R2 = 1 - SSR/SST

    sigma2, cov, se = variance(transform, SSR, x, T, robust, residual, _lambda, sigma2_c, sigma2_u)
    t_values = b_hat/se
    
    names = ['b_hat', 'se', 'sigma2', 't_values', 'R2', 'cov']
    results = [b_hat, se, sigma2, t_values, R2, cov]
    return dict(zip(names, results))

    
def est_ols( y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Estimates y on x by ordinary least squares, returns coefficents

    Args:
        >> y (np.array): Dependent variable (Needs to have shape 2D shape)
        >> x (np.array): Independent variable (Needs to have shape 2D shape)

    Returns:
        np.array: Estimated beta coefficients.
    """
    return la.inv(x.T@x)@(x.T@y)

def variance( 
        transform: str, 
        SSR: float, 
        x: np.ndarray, 
        T: int, 
        robust: bool, 
        residual: np.ndarray,
        _lambda: float,
        sigma2_c: float,
        sigma2_u: float
    ) -> tuple:
    """Calculates the covariance and standard errors from the OLS
    estimation.

    Args:
        >> transform (str): Defaults to ''. If the data is transformed in 
        any way, the following transformations are allowed:
            '': No transformations
            'fd': First-difference
            'be': Between transformation
            'fe': Within transformation
            're': Random effects estimation
        >> SSR (float): Sum of squared residuals
        >> x (np.array): Dependent variables from regression
        >> t (int): The number of time periods in x.

    Raises:
        Exception: If invalid transformation is provided, returns
        an error.

    Returns:
        tuple: Returns the error variance (mean square error), 
        covariance matrix and standard errors.
    """

    # Store n and k, used for DF adjustments.
    K = x.shape[1]
    if transform in ('', 'fd', 'be'):
        N = x.shape[0]
    else:
        N = x.shape[0]/T


    # Calculate sigma2
    if transform in ('', 'fd', 'be'):
        sigma2 = (np.array(SSR/(N - K)))
    elif transform.lower() == 'fe':
        sigma2 = np.array(SSR/(N * (T - 1) - K))
    elif transform.lower() == 're':
        sigma2 = np.array(SSR/(T * N - K))
    else:
        raise Exception('Invalid transform provided.')
    
    cov = sigma2*la.inv(x.T@x)

    # Calculate robust covariance matrix
    if robust is True:
        if transform in ('','fd','be',):
            out = 0
            for i in range(len(x)):
                xi = x[i,:].reshape(-1,1)
                resi = residual[i,:].reshape(-1,1)
                out += xi@resi@resi.T@xi.T
            cov = la.inv(x.T@x)@(out)@la.inv(x.T@x)
        
        if transform.lower() == 'fe':
            out = 0
            for i in range(int(N)):
                xi = x[T*i:T*(i+1),:]
                ui = residual[T*i:T*(i+1)]
                out += xi.T@ui@ui.T@xi
            cov = la.inv(x.T@x)@(out)@la.inv(x.T@x) # Equation 10.59 Wooldridge (2010)
        
        if transform.lower() == 're':
            residual_split = np.split(residual,N)   # Grouping residuals into N blocks
            sigmahat = sigma2_c*np.ones((T,T)) + sigma2_u*np.eye(T)
            x_split = np.split(x,N)
            A = 0
            B = 0
            for i in range(int(N)):
                A += x_split[i].T@la.inv(sigmahat)@x_split[i]
                B += x_split[i].T@la.inv(sigmahat)@residual_split[i]@residual_split[i].T@la.inv(sigmahat)@x_split[i]
            cov = la.inv(A)@B@la.inv(A)                             # Equation 7.52 Wooldridge (2010)
            
    se = np.sqrt(cov.diagonal()).reshape(-1, 1)
    return sigma2, cov, se


def print_table(
        labels: tuple,
        results: dict,
        headers=["", "Beta", "Se", "t-values"],
        title="Results",
        _lambda:float=None,
        **kwargs
    ) -> None:
    """Prints a nice looking table, must at least have coefficients, 
    standard errors and t-values. The number of coefficients must be the
    same length as the labels.

    Args:
        >> labels (tuple): Touple with first a label for y, and then a list of 
        labels for x.
        >> results (dict): The results from a regression. Needs to be in a 
        dictionary with at least the following keys:
            'b_hat', 'se', 't_values', 'R2', 'sigma2'
        >> headers (list, optional): Column headers. Defaults to 
        ["", "Beta", "Se", "t-values"].
        >> title (str, optional): Table title. Defaults to "Results".
        _lambda (float, optional): Only used with Random effects. 
        Defaults to None.
    """
    
    # Unpack the labels
    label_y, label_x = labels
    
    # Create table, using the label for x to get a variable's coefficient,
    # standard error and t_value.
    table = []
    for i, name in enumerate(label_x):
        row = [
            name, 
            results.get('b_hat')[i], 
            results.get('se')[i], 
            results.get('t_values')[i]
        ]
        table.append(row)
    
    # Print the table
    print(title)
    print(f"Dependent variable: {label_y}\n")
    print(tabulate(table, headers, **kwargs))
    
    # Print extra statistics of the model.
    print(f"R\u00b2 = {results.get('R2').item():.3f}")
    print(f"\u03C3\u00b2 = {results.get('sigma2').item():.3f}")
    if _lambda: 
        print(f'\u03bb = {_lambda.item():.3f}')


def perm( Q_T: np.ndarray, A: np.ndarray, T=0) -> np.ndarray:
    """Takes a transformation matrix and performs the transformation on 
    the given vector or matrix.

    Args:
        Q_T (np.array): The transformation matrix. Needs to have the same
        dimensions as number of years a person is in the sample.
        
        A (np.array): The vector or matrix that is to be transformed. Has
        to be a 2d array.

    Returns:
        np.array: Returns the transformed vector or matrix.
    """
    # We can infer t from the shape of the transformation matrix.
    if T==0:
        T = Q_T.shape[1]

    # Initialize the numpy array
    Z = np.array([[]])
    Z = Z.reshape(0, A.shape[1])

    # Loop over the individuals, and permutate their values.
    for i in range(int(A.shape[0]/T)):
        Z = np.vstack((Z, Q_T@A[i*T: (i + 1)*T]))
    return Z


def significance(params: np.ndarray, se: np.ndarray):
    """Chekcs the significance levels

    Args:
        >> params (np.array): Estimated parameters
        >> se (np.array): Estimated standard errors

    Returns:
        array: Returns array with level, at which estimated parameters are significantly different from zero. 
        0 corresponds to estimates being insignificant.
    """
    out = params.copy()
    sig_1 = norm.isf(0.005)
    sig_5 = norm.isf(0.025)
    sig_10 = norm.isf(0.05)
    out[out >= sig_10*se] = 10
    out[out >= sig_5*se] = 5
    out[out >= sig_1*se] = 1
    out[(out != 10) & (out != 5) & (out != 1)] = 0
    return out.astype(int)