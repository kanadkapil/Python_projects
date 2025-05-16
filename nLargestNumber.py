a=int(input("enter a number:"))
b=int(input("enter b number:"))
c=int(input("enter c number:"))

if a>b and a>c:
    print("a is largest: ",a)
elif b>a and b>c:
    print("b is largest: ", b)
else:
    print("c is largest: ", c)