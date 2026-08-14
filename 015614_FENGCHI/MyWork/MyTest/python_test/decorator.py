# coding: utf-8
# Author：fengchi863
# Date ：2020/5/25 9:38

'''
def log(func):
    def wrapper(*args, **kwargs):
        print('call %s():' % func.__name__)
        return func(*args, **kwargs)
    return wrapper
'''

def log(text):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log('excute')
def now():
    print('2020-05-20')

if __name__ == '__main__':
    now()