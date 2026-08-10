import platform
import os

# warehouse paths & runtime
if platform.system() == 'Windows':
    private_root = r'A:/'
    public_root = r'Z:/'
    private_python_path = 'python'
elif platform.system() == 'Linux':
    private_root = '/data/group/800080'
    public_root = '/data/group/800080'
    private_python_path = '/data/user/012245/anaconda3/bin/python'
else:
    raise NotImplementedError

# public tank
public_h5root = os.path.normpath(os.path.join(public_root, 'prod'))
