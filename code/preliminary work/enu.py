import key_rec

n = 32

def add(x,y):
    return (x+y)%n;

for i in range(n):
    dl = 1 << add(i,2);
    dr = (1 << i) ^ (1 << add(i,4))
    delta_in = (dl << 32) ^ dr
    dl = (1 << i) ^ (1 << add(i,4)) ^ (1 << add(i,8))
    dr = 1 << add(i,6)
    delta_out = (dl << 32) ^ dr
    key_rec.auto_key_guess(4, 4, 23, 64, 128, delta_in, delta_out)
    print('-----------------------------------------');