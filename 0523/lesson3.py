import random

# 產生 1~100 的隨機整數
answer = random.randint(1, 100)
print(answer)
count = 0
lower_bound = 1
upper_bound = 100

print("=== 猜數字遊戲 ===")
print("請猜一個 1 到 100 的數字")

while True:
    guess = int(input("請輸入數字: "))
    
    count += 1

    if guess > answer:
        upper_bound = min(upper_bound, guess)
        print(f"太高了，在{lower_bound}~{guess}之間")
    elif guess < answer:
        lower_bound = max(lower_bound, guess)
        print(f"太低了，在{guess}~{upper_bound}之間")
    else:
        print(f"恭喜猜對了！答案是 {answer}")
        print(f"你總共猜了 {count} 次")
        break