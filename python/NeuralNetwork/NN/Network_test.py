import unittest

import numpy as np

from NeuralNetwork.NN.ConvLayer import ConvLayer, MaxPoolLayer
from NeuralNetwork.NN.FullyConnected import FullyConnectedLayer
from NeuralNetwork.NN.Network import Network, check_layers
from NeuralNetwork.NN.Util import ReshapeLayer


class NetworkTestCase(unittest.TestCase):

    def testDataShapeCheck(self):
        layers = [
            FullyConnectedLayer(input_size=1, output_size=10),
            FullyConnectedLayer(input_size=20, output_size=20),
            FullyConnectedLayer(input_size=20, output_size=10),
            FullyConnectedLayer(input_size=10, output_size=1),
        ]
        self.assertRaises(ValueError, check_layers, layers)

        layers = [
            FullyConnectedLayer(input_size=1, output_size=10),
            FullyConnectedLayer(input_size=10, output_size=20),
            FullyConnectedLayer(input_size=20, output_size=10),
            FullyConnectedLayer(input_size=10, output_size=1),
        ]

        try:
            check_layers(layers)
        except ValueError:
            self.fail(msg="Layers check failed")

    def test_forward_prop(self):

        layers = [
            ReshapeLayer(newshape=[-1, 28, 28, 1]),
            ConvLayer(in_channels=1, out_channels=16, kernel_size=3),   # [? 28 28 16]
            MaxPoolLayer(size=2),                                       # [? 14 14 16]
            ConvLayer(in_channels=16, out_channels=32, kernel_size=3),  # [? 14 14 32]
            MaxPoolLayer(size=2),                                       # [?  7  7 32]
            # ConvLayer(in_channels=32, out_channels=64, kernel_size=3),  # [?  7  7 64]
            # MaxPoolLayer(size=2),
            ReshapeLayer(newshape=[-1, 32*7*7]),
            FullyConnectedLayer(input_size=32*7*7, output_size=64),
            FullyConnectedLayer(input_size=64, output_size=10),
        ]

        n = Network(layers)

        # create test data
        x = np.random.rand(10, 28, 28)

        y = n.forward(x)