
import torch
from time import time
import numpy as np
import os

from src.model_BEV_TXT import compile_model_bevtxt
from src.data import compile_data
from src.tools import MultiLoss, get_val_info_new


def train(args):

    max_grad_norm = 5.0
    grid_conf = {'xbound': args.xbound, 'ybound': args.ybound,
                 'zbound': args.zbound,'dbound': args.dbound,}
    data_aug_conf = {
                    'resize_lim': args.resize_lim,
                    'final_dim': args.final_dim,
                    'rot_lim': args.rot_lim,
                    'H': args.H, 'W': args.W,
                    'rand_flip': args.rand_flip,
                    'bot_pct_lim': args.bot_pct_lim,
                    'cams': ['CAM_FRONT_LEFT', 'CAM_FRONT', 'CAM_FRONT_RIGHT',
                             'CAM_BACK_LEFT', 'CAM_BACK', 'CAM_BACK_RIGHT'],
                    'Ncams': args.ncams,
                }
    trainloader, valloader = compile_data(args.version, args.dataroot, data_aug_conf=data_aug_conf,
                                          grid_conf=grid_conf, bsz=args.bsize, nworkers=args.nworkers,
                                          parser_name='segmentationdata')

    if not os.path.exists(args.logdir):
        os.mkdir(args.logdir)
    device = torch.device('cpu') if args.gpuid < 0 else torch.device(f'cuda:{args.gpuid}')

    model = compile_model_bevtxt(args.bsize, grid_conf, data_aug_conf, outC=args.seg_classes)
    if args.checkpoint:
        print('loading', args.checkpoint)
        model.load_state_dict(torch.load(args.checkpoint), strict=False)
    model.to(device)

    opt = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wdecay)

    counter = 0
    for epoch in range(args.nepochs):
        print('--------------Epoch: {}--------------'.format(epoch))
        np.random.seed()
        model.train()
        for batchi, (imgs, rots, trans, intrins, post_rots, post_trans, binimgs, acts, descs) in enumerate(trainloader):
            t0 = time()
            opt.zero_grad()
            bev_pres, act_pres, desc_pres = model(imgs.to(device),
                    rots.to(device),
                    trans.to(device),
                    intrins.to(device),
                    post_rots.to(device),
                    post_trans.to(device),)
            binimgs = binimgs.to(device)
            acts = acts.to(device)
            descs = descs.to(device)

            loss = MultiLoss(bev_pres, act_pres, desc_pres, binimgs, acts, descs, args)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            opt.step()
            counter += 1
            t1 = time()

            if counter % 200 == 0:
                print('Counter{} Train_Loss: {}'.format(counter, loss.item()))

        # val_info
        iou_info, category_act, category_desc, act_overall, desc_overall, \
        act_mean, desc_mean = get_val_info_new(model, valloader, device)
        iou_info = str(iou_info)
        print(iou_info)
        AD_info = """
                F1_Action: {0}
                F1_Description: {1}
                Action_overall: {2}
                Description_overall: {3}
                Action_mean: {4}
                Description_mean: {5}
                """.format(category_act, category_desc, act_overall, desc_overall, act_mean, desc_mean)
        print(AD_info)

        # Log the val info
        results_txt = './result.txt'
        with open(results_txt, "a") as f:
            f.write('epoch{}'.format(epoch) + iou_info + '\n' + 'F1_info: ' + AD_info + "\n\n")

        # Save the weight
        mname = os.path.join(args.logdir, "model{}.pt".format(epoch))
        print('saving', mname)
        torch.save(model.state_dict(), mname)
        model.train()


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="pytorch training")
    # General Setting
    parser.add_argument("--version", default='trainval', help='[trainval, mini]')
    parser.add_argument("--dataroot", default="/path/to/the/dataset/")
    parser.add_argument("--nepochs", default=50, type=int)
    parser.add_argument("--gpuid", default=1, type=int)
    parser.add_argument("--logdir", default='./result-log/', help='path for the log file')
    parser.add_argument("--bsize", default=6, type=int) # 10 for b0/b1; 9 for b2; 8 for b3; 6 for b4; 4 for b5; 3 for b6; 2 for b7
    parser.add_argument("--nworkers", default=10, type=int)
    parser.add_argument('--lr', default=1e-4, type=float, help='initial learning rate')
    parser.add_argument('--wdecay', default=1e-8, type=float, help='weight decay')
    parser.add_argument('--checkpoint', default='')
    parser.add_argument('--examplef', default='./examples', help='file for viz images')
    parser.add_argument('--seg_classes', default=4, help='number of class in segmentation')

    parser.add_argument('--xbound', default=[-50.0, 50.0, 0.5], help='grid configuration')
    parser.add_argument('--ybound', default=[-50.0, 50.0, 0.5], help='grid configuration')
    parser.add_argument('--zbound', default=[-10.0, 10.0, 20.0], help='grid configuration')
    parser.add_argument('--dbound', default=[4.0, 45.0, 1.0], help='grid configuration')
    parser.add_argument('--H', default=900, type=int)
    parser.add_argument('--W', default=1600, type=int)
    parser.add_argument('--resize_lim', default=(0.193, 0.225))
    parser.add_argument('--final_dim', default=(128, 352))
    parser.add_argument('--bot_pct_lim', default=(0.0, 0.22))
    parser.add_argument('--rot_lim', default=(-5.4, 5.4))
    parser.add_argument('--rand_flip', default=False, type=bool)
    parser.add_argument('--ncams', default=6, type=int)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    train(args)