def printPascal(n):

    for i in range(n+1):
        c=1
        for j in range(1, i+1):
            print(c, sep=' ', end='')
            c=c*(i-j)//j
        print()
#driver code
n = int(input("num: "))
printPascal(n)
