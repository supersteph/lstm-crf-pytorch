import torch
import numpy as np
a = torch.load("trans.pt").detach().cpu().numpy()
b = np.array([[-10000.]*14]*14)
for i in range(11):
	for j in range(11):
		b[i][j]= a[i][j]

#to EOS
b[2][11]=a[2][3]
b[2][12]=a[2][4]
b[2][13]=a[2][3]

#only 0 can go to first 0
cur = [-10000]*14
cur[1] = a[3][1]
cur[3] = a[3][3]
b[3] = cur

#rest of tags only want 0 to them
for i in range(4,11):
	for j in range(11):
		if j != 3:
			b[i][j] = -10000

#first zero
b[11] = np.concatenate((a[3],[a[3][3],-10000, -10000]),axis=0)
b[11][3] = -10000
b[11][1]=-10000

#other one
cur = [-10000]*14
cur[4] = a[4][4]
cur[11] = a[4][3]
b[12] = cur

#other zero

b[13][13] = a[3][3]
b[13][12] = a[3][4]
tensor = torch.FloatTensor(b)
print(tensor.type())
torch.save(tensor,"trans.ptb")