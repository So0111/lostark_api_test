import numpy as np

# 1. Joint Probability P(X, Y)
raw_data = np.array([[0.1, 0.2, 0.1],
                     [0.2, 0.1, 0.3]])
joint_prob = raw_data / np.sum(raw_data)

print("1. Joint Probability P(X, Y):\n", joint_prob)

# 2. Marginal Probability
prob_x = np.sum(joint_prob, axis=1)  # 행 방향 합산 -> P(X)
prob_y = np.sum(joint_prob, axis=0)  # 열 방향 합산 -> P(Y)

print("Sum Rule - P(X):", prob_x)
print("Sum Rule - P(Y):", prob_y)

# 3. Conditional Probability
cond_x_given_y = joint_prob / prob_y
cond_y_given_x = joint_prob / prob_x[:, None]

print("Conditional Probability P(X|Y):\n", cond_x_given_y)
print("Conditional Probability P(Y|X):\n", cond_y_given_x)

# 4. Product Rule 검증
product_rule = cond_x_given_y * prob_y
print("Product Rule (P(X|Y)*P(Y) == P(X,Y)):\n", product_rule)

# 5. Bayes Rule 검증
bayes_rule = (cond_y_given_x * prob_x[:, None]) / prob_y
print("Bayes Rule P(X|Y):\n", bayes_rule)

import numpy as np

EPS = 1e-9  # log(0) 방지용 아주 작은 숫자

# 1000개 데이터 생성
np.random.seed(42)
N = 1000
X_samples = np.random.choice([0, 1], size=N, p=[0.4, 0.6])
Y_samples = np.zeros(N, dtype=int)
for i in range(N):
    if X_samples[i] == 0:
        Y_samples[i] = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
    else:
        Y_samples[i] = np.random.choice([0, 1, 2], p=[0.1, 0.4, 0.5])

# Joint Probability
joint_counts = np.zeros((2, 3))
for x, y in zip(X_samples, Y_samples):
    joint_counts[x, y] += 1
joint_prob = joint_counts / N

# Marginal
prob_x = np.sum(joint_prob, axis=1)
prob_y = np.sum(joint_prob, axis=0)

# Conditional
cond_y_given_x = joint_prob / prob_x[:, None]

# 정보이론
info_X0 = -np.log2(prob_x[0])
print(f"비(X=0)가 올 정보량: {info_X0:.4f} bits")

entropy_Y = -np.sum(prob_y * np.log2(prob_y + EPS))
entropy_X = -np.sum(prob_x * np.log2(prob_x + EPS))
print(f"H(Y): {entropy_Y:.4f} bits")
print(f"H(X): {entropy_X:.4f} bits")

cond_x_given_y = joint_prob / prob_y
cond_entropy_YX = -np.sum(joint_prob * np.log2(cond_y_given_x + EPS))
print(f"조건부 엔트로피 H(Y|X): {cond_entropy_YX:.4f} bits")

P_Y_given_X0 = cond_y_given_x[0]
P_Y_given_X1 = cond_y_given_x[1]
kl_div = np.sum(P_Y_given_X0 * np.log2((P_Y_given_X0 + EPS) / (P_Y_given_X1 + EPS)))
print(f"KL Divergence: {kl_div:.4f} bits")

I_XY = entropy_Y - cond_entropy_YX
print(f"상호정보량 I(X;Y): {I_XY:.4f} bits")