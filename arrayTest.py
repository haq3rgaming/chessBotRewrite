bottom = 3.5
top = 27
step = (top-bottom)/7
print(step)
print({str(i+1): round(bottom + i*step, 3) for i in range(8)})