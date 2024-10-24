# input section
n=input('Enter Fibb Number: ')
l1=n.split(',')
l2=[]

for i in l1:
    l2.append(int(i))

# Took max value and made it 2
m=max(l2)
n=2*m
sum1=0
a=0
b=1
l3=[]

# while loop
while(sum1<n):
    l3.append(sum1)
    a=b
    b=sum1
    sum1=a+b
for i in l2:
    if i in l3:
        print(i, 'Valid')
    else:
        print(i, 'Invalid')
