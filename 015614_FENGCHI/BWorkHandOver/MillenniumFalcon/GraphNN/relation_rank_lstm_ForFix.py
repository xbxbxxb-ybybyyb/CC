import sys
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
import argparse
import copy
import numpy as np
import os
# import psutil
import random
import tensorflow as tf
from time import time
from dataApi.FixFactorRollPrepare import loadFixTensorize
from StrongStockModel.conf.path_config import root_path
import pandas as pd
from MillenniumFalcon.IndustryMatrixDaily import get_relation_matrix,get_historical_matrix
from dataApi.getData import get_daily_1factor
from tqdm import tqdm
import configparser
try:
    from tensorflow.python.ops.nn_ops import leaky_relu
except ImportError:
    from tensorflow.python.framework import ops
    from tensorflow.python.ops import math_ops


    def leaky_relu(features, alpha=0.2, name=None):
        with ops.name_scope(name, "LeakyRelu", [features, alpha]):
            features = ops.convert_to_tensor(features, name="features")
            alpha = ops.convert_to_tensor(alpha, name="alpha")
            return math_ops.maximum(alpha * features, features)

from load_data import load_EOD_data, load_relation_data
from evaluator import evaluate

seed = 123456789
np.random.seed(seed)
tf.set_random_seed(seed)


def get_fix_factor_evaluation(indicator, num, end_index):
    using_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_local_path/available_factor_list.pkl')
    factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{indicator}.pkl')
    inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(using_factor_list)))
    factor_evaluation = factor_evaluation[inter_col]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
    print(f'target eval date {target_date}')
    if 'ret' in indicator:
        print('ret')
        factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
    elif 'ic' in indicator:
        print('ic')
        factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
    else:
        raise Exception('')
    factor_list = factor_evaluation.index.tolist()[:num]
    return sorted(factor_list)

class ReRaLSTM:
    def __init__(self, train_start,train_end,test_start,test_end,factor_eval_indicator, factor_num,
                 relation_name, parameters,out_path, steps=1, epochs=50, batch_size=None, flat=False, gpu=False, in_pro=False,
                 data_path=None):

        seed = 123456789
        random.seed(seed)
        np.random.seed(seed)
        tf.set_random_seed(seed)
        self.out_path = os.path.abspath(out_path)
        self.model_conf_path = f'{self.out_path}_model_conf'
        self.val_path = f'{self.out_path}_val_pred'
        self.factor_list_path = f'{self.out_path}_factor_list'

        for each in [self.out_path, self.model_conf_path, self.val_path, self.factor_list_path]:
            if not os.path.exists(each):
                os.makedirs(each)

        self.train_start, self.train_end, self.test_start, self.test_end = train_start,train_end,test_start,test_end
        factor_list = get_fix_factor_evaluation(factor_eval_indicator, factor_num, train_end)
        pd.to_pickle(factor_list,f'{self.factor_list_path}/{self.train_end}.pkl')
        self.embedding, self.gt_data, self.mask_data, self.date_list, self.time_list, self.tickers = loadFixTensorize(train_start, test_end, factor_list,
                                                                                  limit=0.2, nolimit_type='2d_arr', return_type='multi_dim_arr',
                                                                                  address=data_path)
        self.embedding[~self.mask_data] = 0
        self.gt_data[~self.mask_data] = 0

        # relation data
        rname_tail = {'sector_industry': '_industry_relation.npy',
                      'wikidata': '_wiki_relation.npy'}

        sw = get_daily_1factor('SW1')
        self.rel_encoding = get_historical_matrix(sw.loc[[train_end]],return_type='df')[train_end].reindex(self.tickers,axis=0).reindex(self.tickers,axis=1).fillna(0).values[:,:,None]
        mask_flags = np.equal(np.zeros(self.rel_encoding.shape[:-1], dtype=int),
                              np.sum(self.rel_encoding, axis=2))
        self.rel_mask = np.where(mask_flags, np.ones(self.rel_encoding.shape[:-1]) * -1e9, np.zeros(self.rel_encoding.shape[:-1]))

        print('relation encoding shape:', self.rel_encoding.shape)
        print('relation mask shape:', self.rel_mask.shape)
            #np.load(
            #os.path.join(self.data_path, '..', 'pretrain', emb_fname))
        print('embedding shape:', self.embedding.shape)

        self.parameters = copy.copy(parameters)
        self.steps = steps
        self.epochs = epochs
        self.flat = flat
        self.inner_prod = in_pro
        if batch_size is None:
            self.batch_size = len(self.tickers)
        else:
            self.batch_size = batch_size

        self.valid_index = (self.date_list.index(train_end)-10)*len(self.time_list)
        self.test_index = self.date_list.index(test_start)*len(self.time_list)
        self.trade_dates = self.mask_data.shape[1]
        self.fea_dim = factor_num

        self.gpu = gpu

    def get_batch(self, offset=None):
        if offset is None:
            offset = random.randrange(0, self.valid_index)
        # mask_batch = self.mask_data[:, offset: offset + seq_len + self.steps]
        mask_batch = self.mask_data[:,offset]#np.min(mask_batch, axis=1)
        return self.embedding[:, offset, :], \
                   np.expand_dims(mask_batch, axis=1), \
                   np.expand_dims(
                       self.gt_data[:, offset], axis=1
                   )

    # def get_model(self):
    def get_model(self,dev_name):
        with tf.device(dev_name):
            tf.reset_default_graph()

            seed = 123456789
            random.seed(seed)
            np.random.seed(seed)
            tf.set_random_seed(seed)

            ground_truth = tf.placeholder(tf.float32, [self.batch_size, 1])
            mask = tf.placeholder(tf.float32, [self.batch_size, 1])
            feature = tf.placeholder(tf.float32,
                                     [self.batch_size, self.parameters['unit']])
            # base_price = tf.placeholder(tf.float32, [self.batch_size, 1])
            all_one = tf.ones([self.batch_size, 1], dtype=tf.float32)

            relation = tf.constant(self.rel_encoding, dtype=tf.float32)
            rel_mask = tf.constant(self.rel_mask, dtype=tf.float32)

            rel_weight = tf.layers.dense(relation, units=1,
                                         activation=leaky_relu)

            if self.inner_prod:
                print('inner product weight')
                inner_weight = tf.matmul(feature, feature, transpose_b=True)
                weight = tf.multiply(inner_weight, rel_weight[:, :, -1])
            else:
                print('sum weight')
                head_weight = tf.layers.dense(feature, units=1,
                                              activation=leaky_relu)
                tail_weight = tf.layers.dense(feature, units=1,
                                              activation=leaky_relu)
                weight = tf.add(
                    tf.add(
                        tf.matmul(head_weight, all_one, transpose_b=True),
                        tf.matmul(all_one, tail_weight, transpose_b=True)
                    ), rel_weight[:, :, -1]
                )
            weight_masked = tf.nn.softmax(tf.add(rel_mask, weight), dim=0)
            outputs_proped = tf.matmul(weight_masked, feature)
            if self.flat:
                print('one more hidden layer')
                outputs_concated = tf.layers.dense(
                    tf.concat([feature, outputs_proped], axis=1),
                    units=self.parameters['unit'], activation=leaky_relu,
                    kernel_initializer=tf.glorot_uniform_initializer()
                )
            else:
                outputs_concated = tf.concat([feature, outputs_proped], axis=1)

            # One hidden layer
            return_ratio = tf.layers.dense(
                outputs_concated, units=1, activation=leaky_relu, name='reg_fc',
                kernel_initializer=tf.glorot_uniform_initializer()
            )

            # return_ratio = tf.div(tf.subtract(prediction, base_price), base_price)
            reg_loss = tf.losses.mean_squared_error(
                ground_truth, return_ratio, weights=mask
            )
            pre_pw_dif = tf.subtract(
                tf.matmul(return_ratio, all_one, transpose_b=True),
                tf.matmul(all_one, return_ratio, transpose_b=True)
            )
            gt_pw_dif = tf.subtract(
                tf.matmul(all_one, ground_truth, transpose_b=True),
                tf.matmul(ground_truth, all_one, transpose_b=True)
            )
            mask_pw = tf.matmul(mask, mask, transpose_b=True)
            rank_loss = tf.reduce_mean(
                tf.nn.relu(
                    tf.multiply(
                        tf.multiply(pre_pw_dif, gt_pw_dif),
                        mask_pw
                    )
                )
            )
            loss = reg_loss  # + tf.cast(self.parameters['alpha'], tf.float32) * rank_loss
            optimizer = tf.train.AdamOptimizer(
                learning_rate=self.parameters['lr']
            ).minimize(loss)
        return loss, reg_loss, rank_loss, optimizer,weight_masked,weight,return_ratio,outputs_concated,\
               feature,mask,ground_truth,head_weight,tail_weight,rel_weight

    def train(self,early_stop_round):
        if self.gpu == True:
            device_name = '/gpu:0'
        else:
            device_name = '/cpu:0'
        print('device name:', device_name)
        # tf.device(device_name)
        loss, reg_loss, rank_loss, optimizer, weight_masked, weight, return_ratio, outputs_concated,\
        feature,mask,ground_truth,head_weight,tail_weight,rel_weight = self.get_model(device_name)
        sess = tf.Session()
        saver = tf.train.Saver()
        sess.run(tf.global_variables_initializer())
        best_valid_pred = np.zeros(
            [len(self.tickers), self.test_index - self.valid_index],
            dtype=float
        )
        best_valid_gt = np.zeros(
            [len(self.tickers), self.test_index - self.valid_index],
            dtype=float
        )
        best_valid_mask = np.zeros(
            [len(self.tickers), self.test_index - self.valid_index],
            dtype=float
        )
        best_test_pred = np.zeros(
            [len(self.tickers), self.trade_dates - self.test_index], dtype=float
        )
        best_test_gt = np.zeros(
            [len(self.tickers), self.trade_dates - self.test_index], dtype=float
        )
        best_test_mask = np.zeros(
            [len(self.tickers), self.trade_dates - self.test_index], dtype=float
        )
        best_valid_perf = {
            'mse': np.inf, 'mrrt': 0.0, 'btl': 0.0
        }
        best_test_perf = {
            'mse': np.inf, 'mrrt': 0.0, 'btl': 0.0
        }
        best_valid_loss = np.inf

        batch_offsets = np.arange(start=0, stop=self.valid_index, dtype=int)
        bes_ep_idx = 0
        for i in range(self.epochs):
            t1 = time()
            np.random.shuffle(batch_offsets)
            tra_loss = 0.0
            tra_reg_loss = 0.0
            tra_rank_loss = 0.0
            # bar = tqdm(range(self.valid_index),desc=f'epoch{i}/{int(self.epochs)}')
            bar = list(range(self.valid_index))
            for j in bar:
                emb_batch, mask_batch, gt_batch = self.get_batch(
                    batch_offsets[j])
                feed_dict = {
                    feature: emb_batch,
                    mask: mask_batch.astype('float32'),
                    ground_truth: gt_batch,
                }
                cur_loss, cur_reg_loss, cur_rank_loss, batch_out,cur_weight_masked,cur_weigh,cur_return_ratio,cur_outputs_concated,cur_head_weight,cur_tail_weight, cur_rel_weight = \
                    sess.run((loss, reg_loss, rank_loss, optimizer,weight_masked,weight,return_ratio,outputs_concated,head_weight,tail_weight,rel_weight),
                             feed_dict)
                tra_loss += cur_loss
                tra_reg_loss += cur_reg_loss
                tra_rank_loss += cur_rank_loss
            print('Train Loss:',
                  tra_loss / (self.valid_index),
                  tra_reg_loss / (self.valid_index),
                  tra_rank_loss / (self.valid_index))


            # test on validation set
            cur_valid_pred = np.zeros(
                [len(self.tickers), self.test_index - self.valid_index],
                dtype=float
            )
            cur_valid_gt = np.zeros(
                [len(self.tickers), self.test_index - self.valid_index],
                dtype=float
            )
            cur_valid_mask = np.zeros(
                [len(self.tickers), self.test_index - self.valid_index],
                dtype=float
            )
            val_loss = 0.0
            val_reg_loss = 0.0
            val_rank_loss = 0.0
            for cur_offset in range(self.valid_index,self.test_index):
                emb_batch, mask_batch, gt_batch = self.get_batch(
                    cur_offset)
                feed_dict = {
                    feature: emb_batch,
                    mask: mask_batch,
                    ground_truth: gt_batch,
                }
                cur_loss, cur_reg_loss, cur_rank_loss, cur_rr, = \
                    sess.run((loss, reg_loss, rank_loss,
                              return_ratio), feed_dict)
                val_loss += cur_loss
                val_reg_loss += cur_reg_loss
                val_rank_loss += cur_rank_loss
                cur_valid_pred[:, cur_offset - self.valid_index] = \
                    copy.copy(cur_rr[:, 0])
                cur_valid_gt[:, cur_offset - self.valid_index] = \
                    copy.copy(gt_batch[:, 0])
                cur_valid_mask[:, cur_offset - self.valid_index] = \
                    copy.copy(mask_batch[:, 0])
            print('Valid MSE:',
                  val_loss / (self.test_index - self.valid_index),
                  val_reg_loss / (self.test_index - self.valid_index),
                  val_rank_loss / (self.test_index - self.valid_index))
            cur_valid_perf = evaluate(cur_valid_pred, cur_valid_gt,
                                      cur_valid_mask)
            print('\t Valid preformance:', cur_valid_perf)

            # test on testing set
            cur_test_pred = np.zeros(
                [len(self.tickers), self.trade_dates - self.test_index],
                dtype=float
            )
            cur_test_gt = np.zeros(
                [len(self.tickers), self.trade_dates - self.test_index],
                dtype=float
            )
            cur_test_mask = np.zeros(
                [len(self.tickers), self.trade_dates - self.test_index],
                dtype=float
            )
            test_loss = 0.0
            test_reg_loss = 0.0
            test_rank_loss = 0.0
            for cur_offset in range(self.test_index,self.trade_dates
            ):
                emb_batch, mask_batch, gt_batch = self.get_batch(
                    cur_offset)
                feed_dict = {
                    feature: emb_batch,
                    mask: mask_batch,
                    ground_truth: gt_batch,
                }
                cur_loss, cur_reg_loss, cur_rank_loss, cur_rr = \
                    sess.run((loss, reg_loss, rank_loss,
                              return_ratio), feed_dict)
                test_loss += cur_loss
                test_reg_loss += cur_reg_loss
                test_rank_loss += cur_rank_loss

                cur_test_pred[:, cur_offset - self.test_index] = \
                    copy.copy(cur_rr[:, 0])
                cur_test_gt[:, cur_offset - self.test_index] = \
                    copy.copy(gt_batch[:, 0])
                cur_test_mask[:, cur_offset - self.test_index] = \
                    copy.copy(mask_batch[:, 0])
            print('Test MSE:',
                  test_loss / (self.trade_dates - self.test_index),
                  test_reg_loss / (self.trade_dates - self.test_index),
                  test_rank_loss / (self.trade_dates - self.test_index))
            cur_test_perf = evaluate(cur_test_pred, cur_test_gt, cur_test_mask)
            print('\t Test performance:', cur_test_perf)
            if val_loss / (self.test_index - self.valid_index) < \
                    best_valid_loss:
                best_valid_loss = val_loss / (self.test_index -
                                              self.valid_index)
                best_valid_perf = copy.copy(cur_valid_perf)
                best_valid_gt = copy.copy(cur_valid_gt)
                best_valid_pred = copy.copy(cur_valid_pred)
                best_valid_mask = copy.copy(cur_valid_mask)
                best_test_perf = copy.copy(cur_test_perf)
                best_test_gt = copy.copy(cur_test_gt)
                best_test_pred = copy.copy(cur_test_pred)
                best_test_mask = copy.copy(cur_test_mask)
                bes_ep_idx = i
                saver.save(sess,f'{self.model_conf_path}/{self.train_end}.pkl')
                print('Better valid loss:', best_valid_loss)
            elif (i-bes_ep_idx)>=early_stop_round:
                print('Stop at epoch %d'%i)
            t4 = time()
            print('epoch:', i, ('time: %.4f ' % (t4 - t1)))
        print('\nBest Valid performance:', best_valid_perf)
        print('\tBest Test performance:', best_test_perf)
        sess.close()
        tf.reset_default_graph()
        return best_valid_pred, best_valid_gt, best_valid_mask, \
               best_test_pred, best_test_gt, best_test_mask

    def update_model(self, parameters):
        for name, value in parameters.items():
            self.parameters[name] = value
        return True


if __name__ == '__main__':


    desc = 'train a relational rank lstm model'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-pf', help='param_file',type=str,
                        default='/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
    parser.add_argument('-pi', help='period index', default=0,type=int)
    parser.add_argument('-feval', help='factor eval indictors',default='ic_c')
    parser.add_argument('-l', default=4,type=int,
                        help='length of historical sequence for feature')
    parser.add_argument('-u', default=100,type=int,
                        help='number of hidden units in lstm')
    parser.add_argument('-s', default=1,type=int,
                        help='steps to make prediction')
    parser.add_argument('-epo', default=100,type=int,
                        help='epochs to train')
    parser.add_argument('-r', default=0.001,type=float,
                        help='learning rate')
    parser.add_argument('-a', default=0,type=float,
                        help='alpha, the weight of ranking loss')
    parser.add_argument('-g', '--gpu', type=int, default=1, help='use gpu')

    parser.add_argument('-e', '--feature_path', type=str,
                        default='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                        help='fname for pretrained sequential embedding')
    parser.add_argument('-rn', '--rel_name', type=str,
                        default='sector_industry',
                        help='relation type: sector_industry or wikidata')
    parser.add_argument('-ip', '--inner_prod', type=int, default=0)
    parser.add_argument('-o', '--out_path', type=str, default='/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix')
    args = parser.parse_args()


    args.gpu = (args.gpu == 1)

    args.inner_prod = (args.inner_prod == 1)

    parameters = {'seq': int(args.l), 'unit': int(args.u), 'lr': float(args.r),
                  'alpha': float(args.a)}
    print('arguments:', args)
    print('parameters:', parameters)

    conf = configparser.ConfigParser()
    conf.read(args.pf)
    para_list = eval(conf['period_info']['period_info'])
    print(args)
    train_s,train_e,test_s,test_e = para_list[args.pi][1]
    print(args.pi,para_list[args.pi][1])

    # train_start, train_end, test_start, test_end
    if os.path.exists(f'{args.out_path}/{train_e}.pkl'):
        print(f'{args.out_path}/{train_e}.pkl exist')
    else:
        params = dict(train_start=train_s,train_end=train_e,test_start=test_s,test_end=test_e,factor_eval_indicator=args.feval,
                           factor_num=args.u,
            data_path=args.feature_path,
            relation_name=args.rel_name,
            parameters=parameters,
            steps=1, epochs=args.epo, batch_size=None, gpu=args.gpu,out_path =args.out_path,
            in_pro=args.inner_prod)
        print(params)
        RR_LSTM = ReRaLSTM(**params)
        res = RR_LSTM.train(15)
        pd.to_pickle({'res':res,'idx':[RR_LSTM.date_list,RR_LSTM.tickers,RR_LSTM.time_list],'nolimit':RR_LSTM.mask_data},f'{RR_LSTM.out_path}/{train_e}.pkl')
