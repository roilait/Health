import re
#
def test(**kwargs):
    print(kwargs['a'])
    print(kwargs['b'])


k = {'a': 10, 'b':100}

test(**k)

def is_valid(email):
    reg = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$"
    if re.match(reg, email) is not None:
        return True
    return False


email = 'mou@gmail.com'
print(is_valid(str(email)))

print(len('password1'))

d = {'a': 1, 'b': '    2', 'c': 3}

for key in d.keys():
    #d[key] = str(d[key]).strip()
    print(key, '-', bool(str(d.get(key)).strip()))

a = '12345a'
print(int(a))
