{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%run homework_modules.ipynb"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import torch\n",
    "from torch.autograd import Variable\n",
    "import numpy\n",
    "import unittest"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "class TestLayers(unittest.TestCase):\n",
    "    def test_Linear(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in, n_out = 2, 3, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.Linear(n_in, n_out)\n",
    "            custom_layer = Linear(n_in, n_out)\n",
    "            custom_layer.W = torch_layer.weight.data.numpy()\n",
    "            custom_layer.b = torch_layer.bias.data.numpy()\n",
    "\n",
    "            layer_input = np.random.uniform(-10, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-10, 10, (batch_size, n_out)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "        \n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "            # 3. check layer parameters grad\n",
    "            custom_layer.accGradParameters(layer_input, next_layer_grad)\n",
    "            weight_grad = custom_layer.gradW\n",
    "            bias_grad = custom_layer.gradb\n",
    "            torch_weight_grad = torch_layer.weight.grad.data.numpy()\n",
    "            torch_bias_grad = torch_layer.bias.grad.data.numpy()\n",
    "            self.assertTrue(np.allclose(torch_weight_grad, weight_grad, atol=1e-6))\n",
    "            self.assertTrue(np.allclose(torch_bias_grad, bias_grad, atol=1e-6))\n",
    "\n",
    "    def test_SoftMax(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.Softmax(dim=1)\n",
    "            custom_layer = SoftMax()\n",
    "\n",
    "            layer_input = np.random.uniform(-10, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.random((batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad /= next_layer_grad.sum(axis=-1, keepdims=True)\n",
    "            next_layer_grad = next_layer_grad.clip(1e-5,1.)\n",
    "            next_layer_grad = 1. / next_layer_grad\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-5))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-5))\n",
    "            \n",
    "    def test_LogSoftMax(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.LogSoftmax(dim=1)\n",
    "            custom_layer = LogSoftMax()\n",
    "\n",
    "            layer_input = np.random.uniform(-10, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.random((batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad /= next_layer_grad.sum(axis=-1, keepdims=True)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "    def test_BatchNormalization(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 32, 16\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            slope = np.random.uniform(0.01, 0.05)\n",
    "            alpha = 0.9\n",
    "            custom_layer = BatchNormalization(alpha)\n",
    "            custom_layer.train()\n",
    "            torch_layer = torch.nn.BatchNorm1d(n_in, eps=custom_layer.EPS, momentum=1.-alpha, affine=False)\n",
    "            custom_layer.moving_mean = torch_layer.running_mean.numpy().copy()\n",
    "            custom_layer.moving_variance = torch_layer.running_var.numpy().copy()\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            # please, don't increase `atol` parameter, it's garanteed that you can implement batch norm layer\n",
    "            # with tolerance 1e-5\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-5))\n",
    "\n",
    "            # 3. check moving mean\n",
    "            self.assertTrue(np.allclose(custom_layer.moving_mean, torch_layer.running_mean.numpy()))\n",
    "            # we don't check moving_variance because pytorch uses slightly different formula for it:\n",
    "            # it computes moving average for unbiased variance (i.e var*N/(N-1))\n",
    "            #self.assertTrue(np.allclose(custom_layer.moving_variance, torch_layer.running_var.numpy()))\n",
    "\n",
    "            # 4. check evaluation mode\n",
    "            custom_layer.moving_variance = torch_layer.running_var.numpy().copy()\n",
    "            custom_layer.evaluate()\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            torch_layer.eval()\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "            \n",
    "    def test_Sequential(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            alpha = 0.9\n",
    "            torch_layer = torch.nn.BatchNorm1d(n_in, eps=BatchNormalization.EPS, momentum=1.-alpha, affine=True)\n",
    "            torch_layer.bias.data = torch.from_numpy(np.random.random(n_in).astype(np.float32))\n",
    "            custom_layer = Sequential()\n",
    "            bn_layer = BatchNormalization(alpha)\n",
    "            bn_layer.moving_mean = torch_layer.running_mean.numpy().copy()\n",
    "            bn_layer.moving_variance = torch_layer.running_var.numpy().copy()\n",
    "            custom_layer.add(bn_layer)\n",
    "            scaling_layer = ChannelwiseScaling(n_in)\n",
    "            scaling_layer.gamma = torch_layer.weight.data.numpy()\n",
    "            scaling_layer.beta = torch_layer.bias.data.numpy()\n",
    "            custom_layer.add(scaling_layer)\n",
    "            custom_layer.train()\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.backward(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-5))\n",
    "\n",
    "            # 3. check layer parameters grad\n",
    "            weight_grad, bias_grad = custom_layer.getGradParameters()[1]\n",
    "            torch_weight_grad = torch_layer.weight.grad.data.numpy()\n",
    "            torch_bias_grad = torch_layer.bias.grad.data.numpy()\n",
    "            self.assertTrue(np.allclose(torch_weight_grad, weight_grad, atol=1e-6))\n",
    "            self.assertTrue(np.allclose(torch_bias_grad, bias_grad, atol=1e-6))\n",
    "\n",
    "    def test_Dropout(self):\n",
    "        np.random.seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            p = np.random.uniform(0.3, 0.7)\n",
    "            layer = Dropout(p)\n",
    "            layer.train()\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            self.assertTrue(np.all(np.logical_or(np.isclose(layer_output, 0), \n",
    "                                        np.isclose(layer_output*(1.-p), layer_input))))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            layer_grad = layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            self.assertTrue(np.all(np.logical_or(np.isclose(layer_grad, 0), \n",
    "                                        np.isclose(layer_grad*(1.-p), next_layer_grad))))\n",
    "\n",
    "            # 3. check evaluation mode\n",
    "            layer.evaluate()\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            self.assertTrue(np.allclose(layer_output, layer_input))\n",
    "\n",
    "            # 4. check mask\n",
    "            p = 0.0\n",
    "            layer = Dropout(p)\n",
    "            layer.train()\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            self.assertTrue(np.allclose(layer_output, layer_input))\n",
    "\n",
    "            p = 0.5\n",
    "            layer = Dropout(p)\n",
    "            layer.train()\n",
    "            layer_input = np.random.uniform(5, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(5, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            zeroed_elem_mask = np.isclose(layer_output, 0)\n",
    "            layer_grad = layer.updateGradInput(layer_input, next_layer_grad)        \n",
    "            self.assertTrue(np.all(zeroed_elem_mask == np.isclose(layer_grad, 0)))\n",
    "\n",
    "            # 5. dropout mask should be generated independently for every input matrix element, not for row/column\n",
    "            batch_size, n_in = 1000, 1\n",
    "            p = 0.8\n",
    "            layer = Dropout(p)\n",
    "            layer.train()\n",
    "\n",
    "            layer_input = np.random.uniform(5, 10, (batch_size, n_in)).astype(np.float32)\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            self.assertTrue(np.sum(np.isclose(layer_output, 0)) != layer_input.size)\n",
    "\n",
    "            layer_input = layer_input.T\n",
    "            layer_output = layer.updateOutput(layer_input)\n",
    "            self.assertTrue(np.sum(np.isclose(layer_output, 0)) != layer_input.size)\n",
    "    def test_LeakyReLU(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            slope = np.random.uniform(0.01, 0.05)\n",
    "            torch_layer = torch.nn.LeakyReLU(slope)\n",
    "            custom_layer = LeakyReLU(slope)\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "    def test_ELU(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            alpha = 1.0\n",
    "            torch_layer = torch.nn.ELU(alpha)\n",
    "            custom_layer = ELU(alpha)\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "    def test_SoftPlus(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.Softplus()\n",
    "            custom_layer = SoftPlus()\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "    def test_ClassNLLCriterionUnstable(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.NLLLoss()\n",
    "            custom_layer = ClassNLLCriterionUnstable()\n",
    "\n",
    "            layer_input = np.random.uniform(0, 1, (batch_size, n_in)).astype(np.float32)\n",
    "            layer_input /= layer_input.sum(axis=-1, keepdims=True)\n",
    "            layer_input = layer_input.clip(custom_layer.EPS, 1. - custom_layer.EPS)  # unifies input\n",
    "            target_labels = np.random.choice(n_in, batch_size)\n",
    "            target = np.zeros((batch_size, n_in), np.float32)\n",
    "            target[np.arange(batch_size), target_labels] = 1  # one-hot encoding\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input, target)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(torch.log(layer_input_var), \n",
    "                                                 Variable(torch.from_numpy(target_labels), requires_grad=False))\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, target)\n",
    "            torch_layer_output_var.backward()\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "    def test_ClassNLLCriterion(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 4\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.NLLLoss()\n",
    "            custom_layer = ClassNLLCriterion()\n",
    "\n",
    "            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)\n",
    "            layer_input = torch.nn.LogSoftmax(dim=1)(Variable(torch.from_numpy(layer_input))).data.numpy()\n",
    "            target_labels = np.random.choice(n_in, batch_size)\n",
    "            target = np.zeros((batch_size, n_in), np.float32)\n",
    "            target[np.arange(batch_size), target_labels] = 1  # one-hot encoding\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input, target)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var, \n",
    "                                                 Variable(torch.from_numpy(target_labels), requires_grad=False))\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "\n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, target)\n",
    "            torch_layer_output_var.backward()\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "            \n",
    "    def test_adam_optimizer(self):\n",
    "        state = {}  \n",
    "        config = {'learning_rate': 1e-3, 'beta1': 0.9, 'beta2':0.999, 'epsilon':1e-8}\n",
    "        variables = [[np.arange(10).astype(np.float64)]]\n",
    "        gradients = [[np.arange(10).astype(np.float64)]]\n",
    "        adam_optimizer(variables, gradients, config, state)\n",
    "        self.assertTrue(np.allclose(state['m'][0], np.array([0. , 0.1, 0.2, 0.3, 0.4, 0.5, \n",
    "                                                             0.6, 0.7, 0.8, 0.9])))\n",
    "        self.assertTrue(np.allclose(state['v'][0], np.array([0., 0.001, 0.004, 0.009, 0.016, 0.025, \n",
    "                                                             0.036, 0.049, 0.064, 0.081])))\n",
    "        self.assertTrue(state['t'] == 1)\n",
    "        self.assertTrue(np.allclose(variables[0][0], np.array([0., 0.999, 1.999, 2.999, 3.999, 4.999, \n",
    "                                                               5.999, 6.999, 7.999, 8.999])))\n",
    "        adam_optimizer(variables, gradients, config, state)\n",
    "        self.assertTrue(np.allclose(state['m'][0], np.array([0., 0.19, 0.38, 0.57, 0.76, 0.95, 1.14, \n",
    "                                                             1.33, 1.52, 1.71])))\n",
    "        self.assertTrue(np.allclose(state['v'][0], np.array([0., 0.001999, 0.007996, 0.017991, \n",
    "                                                             0.031984, 0.049975, 0.071964, 0.097951, \n",
    "                                                             0.127936, 0.161919])))\n",
    "        self.assertTrue(state['t'] == 2)\n",
    "        self.assertTrue(np.allclose(variables[0][0], np.array([0., 0.998, 1.998, 2.998, 3.998, 4.998, \n",
    "                                                               5.998, 6.998, 7.998, 8.998])))\n",
    "    \n",
    "suite = unittest.TestLoader().loadTestsFromTestCase(TestLayers)\n",
    "unittest.TextTestRunner(verbosity=2).run(suite)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "class TestAdvancedLayers(unittest.TestCase):\n",
    "    def test_Conv2d(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in, n_out = 2, 3, 4\n",
    "        h,w = 5,6\n",
    "        kern_size = 3\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.Conv2d(n_in, n_out, kern_size, padding=1)\n",
    "            custom_layer = Conv2d(n_in, n_out, kern_size)\n",
    "            custom_layer.W = torch_layer.weight.data.numpy() # [n_out, n_in, kern, kern]\n",
    "            custom_layer.b = torch_layer.bias.data.numpy()\n",
    "\n",
    "            layer_input = np.random.uniform(-1, 1, (batch_size, n_in, h,w)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-1, 1, (batch_size, n_out, h, w)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "        \n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "            \n",
    "            # 3. check layer parameters grad\n",
    "            custom_layer.accGradParameters(layer_input, next_layer_grad)\n",
    "            weight_grad = custom_layer.gradW\n",
    "            bias_grad = custom_layer.gradb\n",
    "            torch_weight_grad = torch_layer.weight.grad.data.numpy()\n",
    "            torch_bias_grad = torch_layer.bias.grad.data.numpy()\n",
    "            #m = ~np.isclose(torch_weight_grad, weight_grad, atol=1e-5)\n",
    "            self.assertTrue(np.allclose(torch_weight_grad, weight_grad, atol=1e-6, ))\n",
    "            self.assertTrue(np.allclose(torch_bias_grad, bias_grad, atol=1e-6))\n",
    "            \n",
    "    def test_MaxPool2d(self):\n",
    "        np.random.seed(42)\n",
    "        torch.manual_seed(42)\n",
    "\n",
    "        batch_size, n_in = 2, 3\n",
    "        h,w = 4,6\n",
    "        kern_size = 2\n",
    "        for _ in range(100):\n",
    "            # layers initialization\n",
    "            torch_layer = torch.nn.MaxPool2d(kern_size)\n",
    "            custom_layer = MaxPool2d(kern_size)\n",
    "\n",
    "            layer_input = np.random.uniform(-10, 10, (batch_size, n_in, h,w)).astype(np.float32)\n",
    "            next_layer_grad = np.random.uniform(-10, 10, (batch_size, n_in, \n",
    "                                                          h // kern_size, w // kern_size)).astype(np.float32)\n",
    "\n",
    "            # 1. check layer output\n",
    "            custom_layer_output = custom_layer.updateOutput(layer_input)\n",
    "            layer_input_var = Variable(torch.from_numpy(layer_input), requires_grad=True)\n",
    "            torch_layer_output_var = torch_layer(layer_input_var)\n",
    "            self.assertTrue(np.allclose(torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6))\n",
    "        \n",
    "            # 2. check layer input grad\n",
    "            custom_layer_grad = custom_layer.updateGradInput(layer_input, next_layer_grad)\n",
    "            torch_layer_output_var.backward(torch.from_numpy(next_layer_grad))\n",
    "            torch_layer_grad_var = layer_input_var.grad\n",
    "            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))\n",
    "\n",
    "\n",
    "suite = unittest.TestLoader().loadTestsFromTestCase(TestAdvancedLayers)\n",
    "unittest.TextTestRunner(verbosity=2).run(suite)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    " "
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}