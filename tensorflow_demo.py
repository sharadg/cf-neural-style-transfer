import tensorflow as tf
from tensorflow.python.client import device_lib

print(device_lib.list_local_devices())

# Matrix Multiplication
mat = tf.random_normal((10000, 10000), dtype=tf.float32)
prod = tf.matmul(mat, tf.transpose(mat))
init = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)
    print(sess.run(prod))
