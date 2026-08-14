# @Time : 2021/11/23 14:13
# @Author : Zhichen Lu
# @File : seesGraphTst.py
import tensorflow as tf
import numpy as np

def get_sees():
    # x = tf.constant([[37.0, -23.0], [1.0, 4.0]])
    x = tf.placeholder(tf.float32,[2,2])
    w = tf.Variable(tf.random_uniform([2, 2]))
    y = tf.matmul(x, w)
    output = tf.nn.softmax(y)
    init_op = w.initializer



      # Evaluate `output`. `sess.run(output)` will return a NumPy array containing
      # the result of the computation.
      # print(sess.run(output))
    return output,init_op,x
  # Evaluate `y` and `output`. Note that `y` will only be computed once, and its
  # result used both to return `y_val` and as an input to the `tf.nn.softmax()`
  # op. Both `y_val` and `output_val` will be NumPy arrays.
  # y_val, output_val = sess.run([y, output])
op,ini_op,x_ = get_sees()

sess = tf.Session()
# sess.run(ini_op)
# print(sess.run((op), {x_: np.array([[37.0, -23.0], [1.0, 4.0]], dtype='float32')}))
saver = tf.train.Saver()
# saver.save(sess,'/data/user/015664/temp/test_tf_model.pkl')
saver.restore(sess,'/data/user/015664/temp/test_tf_model.pkl')
# ses.run(op)