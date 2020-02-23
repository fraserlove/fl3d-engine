import structures # Importing Matrix and Point objects from math_structures module

""" Provides mathematical functions for used in math structures """

""" Multiplies two matrices together if they are conformable """
def multiply(matrix_1, matrix_2):
    # Checks to see if the object is a point so that this function can be overloaded
    # to include support for multiplication between Point3D and Matrix objects
    matrix_1, matrix_2 = conform_matrices(matrix_1, matrix_2)
        
    if matrix_1.no_cols() != matrix_2.no_rows():
        print("ERROR: Matrix 1's columns do not match Matrix 2's rows")
        return None
    result = structures.Matrix(matrix_1.no_rows(), matrix_2.no_cols())

    # Finding the dot product of the row of matrix 1 and the column of matrix 2 for each element in the new matrix
    for y in range(matrix_1.no_rows()):
        for x in range(matrix_2.no_cols()):
            sum = 0
            for i in range(matrix_1.no_cols()):
                sum += matrix_1.access_index(y, i) * matrix_2.access_index(i, x)
            result.set_index(y, x, sum)
    return result

def h_stack(matrix_1, matrix_2):
    """ Adds matrix_2 to the right columns of matrix_1 """
    matrix_1, matrix_2 = conform_matrices(matrix_1, matrix_2)
    result = structures.Matrix(matrix_1.no_rows(), matrix_1.no_cols() + matrix_2.no_cols())
    for y in range(matrix_1.no_rows()):
        result.set_row(y, matrix_1.access_row(y) + matrix_2.access_row(y))
    return result

def conform_matrices(matrix_1, matrix_2):
    """ Checks to see if the matrix_1 or matrix_2 are Point3D objects and if true converts them to matrices """
    if isinstance(matrix_1, structures.Point3D):
        matrix_1 = matrix_1.point3d_to_matrix()
    if isinstance(matrix_2, structures.Point3D):
        matrix_2 = matrix_2.point3d_to_matrix()
    return matrix_1, matrix_2