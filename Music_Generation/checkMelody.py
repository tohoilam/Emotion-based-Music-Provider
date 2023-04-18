import tensorflow as tf

tf.compat.v1.enable_eager_execution
print(sum(1 for _ in tf.data.TFRecordDataset("training_input/old/Happiness/training_melodies.tfrecord")))
print(sum(1 for _ in tf.data.TFRecordDataset("training_input/old/Happiness/eval_melodies.tfrecord")))