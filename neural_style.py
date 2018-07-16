# # Deep Learning & Art: Neural Style Transfer
#

import os
import sys
import scipy.io
import io
import scipy.misc
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from nst_utils import (
    load_vgg_model,
    generate_noise_image,
    reshape_and_normalize_image,
    save_image,
)

STYLE_LAYERS = [
    ("conv1_1", 0.2),
    ("conv2_1", 0.2),
    ("conv3_1", 0.2),
    ("conv4_1", 0.2),
    ("conv5_1", 0.2),
]


class NeuralStyleTransfer(object):
    def __init__(self):
        self._session = None

    def compute_content_cost(self, a_C, a_G):
        """
        Computes the content cost
        
        Arguments:
        a_C -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing content of the image C 
        a_G -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing content of the image G

        Returns: 
        J_content -- scalar that you compute using equation 1 above.
        """

        # Retrieve dimensions from a_G (≈1 line)
        _, n_H, n_W, n_C = a_C.shape.as_list()

        # Reshape a_C and a_G (≈2 lines)
        a_C_unrolled = tf.reshape(a_C, [n_H * n_W, n_C])
        a_G_unrolled = tf.reshape(a_G, [n_H * n_W, n_C])

        # compute the cost with tensorflow (≈1 line)
        J_content = (
                1
                / (4 * n_H * n_W * n_C)
                * tf.reduce_sum(tf.square(tf.subtract(a_C_unrolled, a_G_unrolled)))
        )

        return J_content

    def gram_matrix(self, A):
        """
        Argument:
        A -- matrix of shape (n_C, n_H*n_W)
        
        Returns:
        GA -- Gram matrix of A, of shape (n_C, n_C)
        """

        GA = tf.matmul(A, tf.transpose(A))

        return GA

    def compute_layer_style_cost(self, a_S, a_G):
        """
        Arguments:
        a_S -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing style of the image S 
        a_G -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing style of the image G
        
        Returns: 
        J_style_layer -- tensor representing a scalar value, style cost defined above by equation (2)
        """

        # Retrieve dimensions from a_G (≈1 line)
        _, n_H, n_W, n_C = a_S.shape.as_list()

        # Reshape the images to have them of shape (n_C, n_H*n_W) (≈2 lines)
        a_S = tf.transpose(tf.reshape(a_S, [n_H * n_W, n_C]))
        a_G = tf.transpose(tf.reshape(a_G, [n_H * n_W, n_C]))

        # Computing gram_matrices for both images S and G (≈2 lines)
        GS = self.gram_matrix(a_S)
        GG = self.gram_matrix(a_G)

        # Computing the loss (≈1 line)
        J_style_layer = (
                1
                / (4 * (n_H * n_W * n_C) ** 2)
                * tf.reduce_sum(tf.square(tf.subtract(GG, GS)))
        )

        return J_style_layer

    def compute_style_cost(self, model, STYLE_LAYERS):
        """
        Computes the overall style cost from several chosen layers
        
        Arguments:
        model -- our tensorflow model
        STYLE_LAYERS -- A python list containing:
                            - the names of the layers we would like to extract style from
                            - a coefficient for each of them
        
        Returns: 
        J_style -- tensor representing a scalar value, style cost defined above by equation (2)
        """

        # initialize the overall style cost
        J_style = 0

        for layer_name, coeff in STYLE_LAYERS:
            # Select the output tensor of the currently selected layer
            out = model[layer_name]

            # Set a_S to be the hidden layer activation from the layer we have selected, by running the session on out
            a_S = self._session.run(out)
            a_S = tf.convert_to_tensor(a_S)

            # Set a_G to be the hidden layer activation from same layer. Here, a_G references model[layer_name]
            # and isn't evaluated yet. Later in the code, we'll assign the image G as the model input, so that
            # when we run the session, this will be the activations drawn from the appropriate layer, with G as input.
            a_G = out

            # Compute style_cost for the current layer
            J_style_layer = self.compute_layer_style_cost(a_S, a_G)

            # Add coeff * J_style_layer of this layer to overall style cost
            J_style += coeff * J_style_layer

        return J_style

    def total_cost(self, J_content, J_style, alpha=10, beta=40):
        """
        Computes the total cost function
        
        Arguments:
        J_content -- content cost coded above
        J_style -- style cost coded above
        alpha -- hyperparameter weighting the importance of the content cost
        beta -- hyperparameter weighting the importance of the style cost
        
        Returns:
        J -- total cost as defined by the formula above.
        """

        J = alpha * J_content + beta * J_style

        return J

    def model_nn(self, content_image, style_image, num_iterations=100, format="jpeg"):

        # Reset the graph
        tf.reset_default_graph()

        # Start interactive session
        self._session = tf.Session()

        # Let's load, reshape, and normalize our "content" image (the Louvre museum picture):

        # content_image = plt.imread("images/taj-mahal.jpg")
        content_image = reshape_and_normalize_image(content_image)

        # Let's load, reshape and normalize our "style" image (Claude Monet's painting):

        # style_image = plt.imread("images/van_gogh_800600.jpg")
        style_image = reshape_and_normalize_image(style_image)

        # initialize the "generated" image as a noisy image created from the content_image. By initializing the pixels of the generated image to be mostly noise but still slightly correlated with the content image, this will help the content of the "generated" image more rapidly match the content of the "content" image. (Feel free to look in `nst_utils.py` to see the details of `generate_noise_image(...)`; to do so, click "File-->Open..." at the upper-left corner of this Jupyter notebook.)

        generated_image = generate_noise_image(content_image)

        # let's load the VGG16 model.

        model = load_vgg_model("images/imagenet-vgg-verydeep-19.mat")

        # Assign the content image to be the input of the VGG model.
        self._session.run(model["input"].assign(content_image))

        # Select the output tensor of layer conv4_2
        out = model["conv4_2"]

        # Set a_C to be the hidden layer activation from the layer we have selected
        a_C = self._session.run(out)
        a_C = tf.convert_to_tensor(a_C)

        # Set a_G to be the hidden layer activation from same layer. Here, a_G references model['conv4_2']
        # and isn't evaluated yet. Later in the code, we'll assign the image G as the model input, so that
        # when we run the session, this will be the activations drawn from the appropriate layer, with G as input.
        a_G = out

        # Compute the content cost
        J_content = self.compute_content_cost(a_C, a_G)

        # At this point, a_G is a tensor and hasn't been evaluated. It will be evaluated and updated at each iteration when we run the Tensorflow graph in model_nn() below.

        # Assign the input of the model to be the "style" image
        self._session.run(model["input"].assign(style_image))

        # Compute the style cost
        J_style = self.compute_style_cost(model, STYLE_LAYERS)

        # Now that you have J_content and J_style, compute the total cost J by calling `total_cost()`. Use `alpha = 10` and `beta = 40`.

        J = self.total_cost(J_content, J_style)

        # You'd previously learned how to set up the Adam optimizer in TensorFlow. Lets do that here, using a learning rate of 2.0.  [See reference](https://www.tensorflow.org/api_docs/python/tf/train/AdamOptimizer)

        # define optimizer (1 line)
        optimizer = tf.train.AdamOptimizer(2.0)

        # define train_step (1 line)
        train_step = optimizer.minimize(J)

        # Implement the model_nn() function which initializes the variables of the tensorflow graph, assigns the input image (initial generated image) as the input of the VGG16 model and runs the train_step for a large number of steps.

        # Initialize global variables (you need to run the session on the initializer)
        self._session.run(tf.global_variables_initializer())

        # Run the noisy input image (initial generated image) through the model. Use assign().
        self._session.run(model["input"].assign(generated_image))

        for i in range(num_iterations):

            # Run the session on the train_step to minimize the total cost
            self._session.run(train_step)

            # Compute the generated image by running the session on the current model['input']
            generated_image = self._session.run(model["input"])

            # Print every 20 iteration.
            if i % 20 == 0:
                Jt, Jc, Js = self._session.run([J, J_content, J_style])
                print("Iteration " + str(i) + " :")
                print("total cost = {:g}".format(Jt))
                print("content cost = {:g}".format(Jc))
                print("style cost = {:g}".format(Js))

                # save current generated image in the "/output" directory
                # save_image("output/" + str(i) + ".jpg", generated_image)

        # save last generated image
        generated_image_bytes = io.BytesIO()
        save_image(generated_image_bytes, generated_image, format=format)
        generated_image_bytes.seek(0)
        #save_image("output/generated_image.jpg", generated_image)

        return generated_image_bytes


if __name__ == "__main__":
    neural_style_transfer = NeuralStyleTransfer()
    content_image = plt.imread("images/taj-mahal.jpg")
    style_image = plt.imread("images/van_gogh_800600.jpg")
    neural_style_transfer.model_nn(content_image, style_image, num_iterations=20)
