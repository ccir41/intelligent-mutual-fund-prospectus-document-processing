# for creating fake load
import numpy as np

def compute_matrix_multiplication():
    matrix1 = np.random.rand(1000, 1000)
    matrix2 = np.random.rand(1000, 1000)
    np.dot(matrix1, matrix2)

if __name__ == "__main__":
    compute_matrix_multiplication()
