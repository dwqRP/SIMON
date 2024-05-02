import random


CONFIG = {
    (32, 64): (32, 0),
    (48, 72): (36, 0),
    (48, 96): (36, 1),
    (64, 96): (42, 2),
    (64, 128): (44, 3),
    (96, 96): (52, 2),
    (96, 144): (54, 3),
    (128, 128): (68, 2),
    (128, 192): (69, 3),
    (128, 256): (72, 4),
}


def get_random_hex(len):
    num = random.randrange(0, 16**len)
    hex_str = hex(num)[2:]
    hex_str = hex_str.zfill(len)
    return hex_str


# int(hex_str, 16)


def get_const_seq(seq_id):
    assert seq_id in range(5)
    seq = []

    st = [0, 0, 0, 0, 1]
    for i in range(62):
        f = st[2] ^ st[4]
        # LFSRs not in "the usual way"
        if seq_id in (0, 2):
            st[3] ^= st[4]
        elif seq_id in (1, 3):
            st[1] ^= st[0]
        res = st.pop()
        st.insert(0, f)
        if seq_id >= 2:
            res ^= i % 2
        seq.append(res)

    return tuple(seq)


class SIMON:
    """
    one of the two lightweight block ciphers designed by NSA
    this one is optimized for hardware implementation
    """

    def __init__(self, block_size, key_size, master_key=None):
        assert (block_size, key_size) in CONFIG
        self.block_size = block_size
        self.key_size = key_size
        self.num_rounds, seq_id = CONFIG[(block_size, key_size)]
        self.begin_round = 0
        self.end_round = self.num_rounds
        self.__const_seq = get_const_seq(seq_id)
        assert len(self.__const_seq) == 62
        self.__dim = block_size >> 1
        self.__mod = 1 << self.__dim
        if master_key is not None:
            self.change_key(master_key)

    def __lshift(self, x, i=1):
        return ((x << i) % self.__mod) | (x >> (self.__dim - i))

    def __rshift(self, x, i=1):
        return ((x << (self.__dim - i)) % self.__mod) | (x >> i)

    def change_key(self, master_key):
        assert 0 <= master_key < (1 << self.key_size)
        c = (1 << self.__dim) - 4
        m = self.key_size // self.__dim
        self.round_key = []
        for i in range(m):
            self.round_key.append(master_key % self.__mod)
            master_key >>= self.__dim
        for i in range(m, self.num_rounds):
            k = self.__rshift(self.round_key[-1], 3)
            if m == 4:
                k ^= self.round_key[-3]
            k ^= self.__rshift(k) ^ self.round_key[-m]
            k ^= c ^ self.__const_seq[(i - m) % 62]
            self.round_key.append(k)

    def __feistel_round(self, l, r, k):
        f = (self.__lshift(l) & self.__lshift(l, 8)) ^ self.__lshift(l, 2)
        return r ^ f ^ k, l

    def encrypt(self, plaintext):
        assert 0 <= plaintext < (1 << self.block_size)
        l = plaintext >> self.__dim
        r = plaintext % self.__mod
        for i in range(self.begin_round, self.end_round):
            l, r = self.__feistel_round(l, r, self.round_key[i])
        ciphertext = (l << self.__dim) | r
        assert 0 <= ciphertext < (1 << self.block_size)
        return ciphertext

    def decrypt(self, ciphertext):
        assert 0 <= ciphertext < (1 << self.block_size)
        l = ciphertext >> self.__dim
        r = ciphertext % self.__mod
        for i in range(self.end_round - 1, self.begin_round - 1, -1):
            r, l = self.__feistel_round(r, l, self.round_key[i])
        plaintext = (l << self.__dim) | r
        assert 0 <= plaintext < (1 << self.block_size)
        return plaintext


def test_linear_key(test_str, r, bsize, ksize, delta, br):
    er = br + r
    # print(br, er - 1)
    n = bsize >> 1
    count = 0
    rsk = []
    print("delta =", hex(delta))
    for i in range(br, er):
        rsk.append([])
        for j in range(n):
            for tries in range(1000):
                z = int(get_random_hex(bsize >> 4), 16)
                k = int(get_random_hex(ksize >> 4), 16)

                my_simon1 = SIMON(bsize, ksize, k)
                my_simon1.begin_round = br
                my_simon1.end_round = er
                # print(my_simon1.round_key)

                my_simon2 = SIMON(bsize, ksize, k)
                my_simon2.begin_round = br
                my_simon2.end_round = er
                my_simon2.round_key[i] ^= 1 << j
                # print(my_simon2.round_key)

                if test_str == "input":
                    y1 = my_simon1.encrypt(z)
                    y1 ^= delta
                    x1 = my_simon1.decrypt(y1)
                    y2 = my_simon2.encrypt(z)
                    y2 ^= delta
                    x2 = my_simon2.decrypt(y2)
                elif test_str == "output":
                    y1 = my_simon1.decrypt(z)
                    y1 ^= delta
                    x1 = my_simon1.encrypt(y1)
                    y2 = my_simon2.decrypt(z)
                    y2 ^= delta
                    x2 = my_simon2.encrypt(y2)

                if x1 != x2:
                    count += 1
                    rsk[i - br].append(j)
                    break

    if test_str == "input":
        temp_str = "kin"
    else:
        temp_str = "kout"
    print(temp_str, ":")
    print("count =", count)
    for i in range(br, er):
        print("Round", i, ":", rsk[i - br])
    return count, rsk


mat = {}


def add(ksize, row1, row2):
    row3 = []
    for i in range(ksize):
        row3.append(row1[i] ^ row2[i])
    return row3


def query(ksize, n, r, pos):
    if (r, pos) in mat:
        return mat[(r, pos)]
    if r < 4:
        vec = [0] * ksize
        # print(len(vec), ksize - (pos + n * r) - 1)
        vec[ksize - (pos + n * r) - 1] = 1
        mat[(r, pos)] = vec
        return vec
    else:
        sub1 = query(ksize, n, r - 4, pos)
        sub2 = add(ksize, sub1, query(ksize, n, r - 3, pos))
        sub3 = add(ksize, sub2, query(ksize, n, r - 1, (pos + 3) % n))
        sub4 = add(ksize, sub3, query(ksize, n, r - 3, (pos + 1) % n))
        vec = add(ksize, sub4, query(ksize, n, r - 1, (pos + 4) % n))
        mat[(r, pos)] = vec
        return vec


def gauss_elimination(
    ksize,
    kin_sz,
    kout_sz,
    begin_round_in,
    end_round_in,
    begin_round_out,
    end_round_out,
    kin,
    kout,
):
    mtx = []
    mat.clear()
    n = ksize >> 2
    sz = kin_sz + kout_sz
    # print(n, sz)
    for i in range(begin_round_in, end_round_in):
        for pos in kin[i - begin_round_in]:
            vec = query(ksize, n, i, pos)
            # print(vec)
            mtx.append(vec)
    for i in range(begin_round_out, end_round_out):
        # print("!!!", kout[i - begin_round_out])
        for pos in kout[i - begin_round_out]:
            vec = query(ksize, n, i, pos)
            # print(vec)
            mtx.append(vec)
    # print(len(mtx))
    # f.write(str(mtx))
    # for row in mtx:
    #     f.write(str(row) + "\n")
    rank = 0
    mpos = 0
    for i in range(sz):
        while mpos < ksize and mtx[i][mpos] == 0:
            find = False
            for j in range(i + 1, sz):
                if mtx[j][mpos] == 1:
                    mtx[i], mtx[j] = mtx[j], mtx[i]
                    find = True
                    break
            # print(find, i)
            if find == False:
                mpos += 1
            else:
                break
        if mpos == ksize:
            break
        for j in range(i + 1, sz):
            if mtx[j][mpos] == 1:
                mtx[j] = add(ksize, mtx[i], mtx[j])
        mpos += 1
        rank += 1

    # print(mtx)
    if len(kin) == 0:
        print("rank of kout:", rank, "/", min(sz, ksize))
    elif len(kout) == 0:
        print("rank of kin:", rank, "/", min(sz, ksize))
    else:
        print("rank of kin cup kout:", rank, "/", min(sz, ksize))
    # print("main_position:", mpos)
    for row in mtx:
        f.write(str(row) + "\n")

    kres = []
    mpos = 0
    for i in range(sz):
        for j in range(i, ksize):
            if mtx[i][j] == 1:
                for k in range(mpos, j):
                    kres.append(ksize - k - 1)
                mpos = j + 1
                break
    if len(kin) > 0 and len(kout) > 0:
        print("size of kin cap kout:", sz - rank)
        print("size of kres:", len(kres))
        print("kres:", kres)


def auto_key_guess(rin, rout, rd, bsize, ksize, delta_in, delta_out):
    kin_sz, kin = test_linear_key("input", rin, bsize, ksize, delta_in, 0)
    kout_sz, kout = test_linear_key("output", rout, bsize, ksize, delta_out, rd + rin)
    gauss_elimination(ksize, kin_sz, 0, 0, rin, 0, 0, kin, [])
    gauss_elimination(ksize, 0, kout_sz, 0, 0, rd + rin, rd + rin + rout, [], kout)
    gauss_elimination(
        ksize, kin_sz, kout_sz, 0, rin, rd + rin, rd + rin + rout, kin, kout
    )
    full_bits = []
    n = bsize >> 1
    for i in range(n):
        full_bits.append(i)
    kex = kout[:]
    kex.append(full_bits)
    print("when add kex1 :")
    gauss_elimination(
        ksize, kin_sz, kout_sz + n, 0, rin, rd + rin, rd + rin + rout + 1, kin, kex
    )
    kex.append(full_bits)
    print("when add kex2 :")
    gauss_elimination(
        ksize, kin_sz, kout_sz + n + n, 0, rin, rd + rin, rd + rin + rout + 2, kin, kex
    )


if __name__ == "__main__":
    f = open("log.txt", "w")
    const_seq = (
        (
            1,
            1,
            1,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            1,
            0,
            1,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            1,
            0,
            1,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
        ),
        (
            1,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            0,
            1,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            0,
        ),
        (
            1,
            0,
            1,
            0,
            1,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            1,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
        ),
        (
            1,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            1,
            0,
            1,
            0,
            1,
            1,
            0,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            1,
            0,
            0,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
        ),
        (
            1,
            1,
            0,
            1,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
        ),
    )
    for i in range(len(const_seq)):
        assert const_seq[i] == get_const_seq(i)

    test_vectors = (
        # block_size, key_size, key, plaintext, ciphertext
        (32, 64, 0x1918111009080100, 0x65656877, 0xC69BE9BB),
        (48, 72, 0x1211100A0908020100, 0x6120676E696C, 0xDAE5AC292CAC),
        (48, 96, 0x1A19181211100A0908020100, 0x72696320646E, 0x6E06A5ACF156),
        (64, 96, 0x131211100B0A090803020100, 0x6F7220676E696C63, 0x5CA2E27F111A8FC8),
        (
            64,
            128,
            0x1B1A1918131211100B0A090803020100,
            0x656B696C20646E75,
            0x44C8FC20B9DFA07A,
        ),
        (
            96,
            96,
            0x0D0C0B0A0908050403020100,
            0x2072616C6C69702065687420,
            0x602807A462B469063D8FF082,
        ),
        (
            96,
            144,
            0x1514131211100D0C0B0A0908050403020100,
            0x74616874207473756420666F,
            0xECAD1C6C451E3F59C5DB1AE9,
        ),
        (
            128,
            128,
            0x0F0E0D0C0B0A09080706050403020100,
            0x63736564207372656C6C657661727420,
            0x49681B1E1E54FE3F65AA832AF84E0BBC,
        ),
        (
            128,
            192,
            0x17161514131211100F0E0D0C0B0A09080706050403020100,
            0x206572656874206E6568772065626972,
            0xC4AC61EFFCDC0D4F6C9C8D6E2597B85B,
        ),
        (
            128,
            256,
            0x1F1E1D1C1B1A191817161514131211100F0E0D0C0B0A09080706050403020100,
            0x74206E69206D6F6F6D69732061207369,
            0x8D2B5579AFC8A3A03BF72A87EFE7B868,
        ),
    )

    for bsize, ksize, key, plain, cipher in test_vectors:
        my_simon = SIMON(bsize, ksize, key)
        encrypted = my_simon.encrypt(plain)
        assert encrypted == cipher
        for i in range(1000):
            encrypted = my_simon.encrypt(encrypted)
        for i in range(1000):
            encrypted = my_simon.decrypt(encrypted)
        decrypted = my_simon.decrypt(encrypted)
        assert decrypted == plain

    print("All tests passed")

    # test_key(test_str, r, bsize, ksize, delta)

    # SIMON64/128

    # 2023 动态聚集效应... 23 Rounds Trail
    # dl = (1 << 19)
    # dr = (1 << 13) ^ (1 << 17) ^ (1 << 21)
    # delta_in = (dl << 32) ^ dr
    # dl = (1 << 13) ^ (1 << 17)
    # dr = (1 << 15)
    # delta_out = (dl << 32) ^ dr
    # auto_key_guess(4, 4, 23, 64, 128, delta_in, delta_out)

    # 2017 Optimal Diff... 23 Rounds Trail
    # dl = 1
    # dr = (1 << 2) ^ (1 << 30)
    # delta_in = (dl << 32) ^ dr
    # dl = (1 << 2) ^ (1 << 6) ^ (1 << 30)
    # dr = 1 << 4
    # delta_out = (dl << 32) ^ dr
    # auto_key_guess(4, 4, 23, 64, 128, delta_in, delta_out)

    # Ours... 22 Rounds Trail
    # dl = (1 << 14) ^ (1 << 18)
    # dr = (1 << 20)
    # delta_in = (dl << 32) ^ dr
    # dl = (1 << 14) ^ (1 << 18)
    # dr = (1 << 16)
    # delta_out = (dl << 32) ^ dr
    # auto_key_guess(4, 4, 22, 64, 128, delta_in, delta_out)

    # Ours... 23 Rounds Trail
    # dl = 1 << 2
    # dr = (1 << 0) ^ (1 << 4)
    # delta_in = (dl << 32) ^ dr
    # dl = (1 << 0) ^ (1 << 4) ^ (1 << 8)
    # dr = 1 << 6
    # delta_out = (dl << 32) ^ dr
    # auto_key_guess(4, 4, 23, 64, 128, delta_in, delta_out)

    # Ours... 24 Rounds Trail
    dl = (1 << 26) ^ (1 << 30)
    dr = 1
    delta_in = (dl << 32) ^ dr
    dl = (1 << 2) ^ (1 << 26) ^ (1 << 30)
    dr = 1
    delta_out = (dl << 32) ^ dr
    auto_key_guess(4, 4, 23, 64, 128, delta_in, delta_out)

    # SIMON128/256

    # 2017 Optimal Diff... 41 Rounds Trail
    # dl = (1 << 6)
    # dr = (1 << 0) ^ (1 << 4) ^ (1 << 8)
    # delta_in = (dl << 64) ^ dr
    # dl = (1 << 0) ^ (1 << 4) ^ (1 << 8)
    # dr = (1 << 6)
    # delta_out = (dl << 64) ^ dr
    # auto_key_guess(4, 4, 41, 128, 256, delta_in, delta_out)

    # 2023 动态聚集效应... 44 Rounds Trail
    # dl = (1 << 12)
    # dr = (1 << 6) ^ (1 << 10) ^ (1 << 14)
    # delta_in = (dl << 64) ^ dr
    # dl = (1 << 20)
    # dr = (1 << 6) ^ (1 << 14) ^ (1 << 18)
    # delta_out = (dl << 64) ^ dr
    # auto_key_guess(4, 5, 44, 128, 256, delta_in, delta_out)

    # SIMON32/64

    # 2015 Observations... 14 Rounds Trail
    # dl = 0
    # dr = (1 << 3)
    # delta_in = (dl << 16) ^ dr
    # dl = (1 << 11)
    # dr = 0
    # delta_out = (dl << 16) ^ dr
    # auto_key_guess(4, 4, 14, 32, 64, delta_in, delta_out)

    # Ours... 14 Rounds Trail
    # dl = 0
    # dr = 1
    # delta_in = (dl << 16) ^ dr
    # dl = (1 << 10)
    # dr = (1 << 8)
    # delta_out = (dl << 16) ^ dr
    # auto_key_guess(4, 4, 14, 32, 64, delta_in, delta_out)

    # SIMON48/96

    # 2015 Observations... 17 Rounds Trail
    # dl = (1 << 7)
    # dr = (1 << 1) ^ (1 << 5) ^ (1 << 9)
    # delta_in = (dl << 24) ^ dr
    # dl = (1 << 1) ^ (1 << 5) ^ (1 << 9)
    # dr = (1 << 7)
    # delta_out = (dl << 24) ^ dr
    # auto_key_guess(4, 4, 17, 48, 96, delta_in, delta_out)

    # Ours... 16 Rounds Trail
    # dl = (1 << 0) ^ (1 << 4)
    # dr = (1 << 6)
    # delta_in = (dl << 24) ^ dr
    # dl = (1 << 0) ^ (1 << 4) ^ (1 << 8)
    # dr = (1 << 6)
    # delta_out = (dl << 24) ^ dr
    # auto_key_guess(4, 4, 16, 48, 96, delta_in, delta_out)

    # Ours... 15 Rounds Trail
    # dl = (1 << 5) ^ (1 << 9)
    # dr = (1 << 11)
    # delta_in = (dl << 24) ^ dr
    # dl = (1 << 11)
    # dr = (1 << 5) ^ (1 << 9)
    # delta_out = (dl << 24) ^ dr
    # auto_key_guess(4, 4, 15, 48, 96, delta_in, delta_out)

    f.close()
