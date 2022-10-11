from pathlib import Path
import cv2
import matplotlib.cm as cm
import torch
import numpy as np


from superglue_lib.models.matching import Matching
from superglue_lib.models.utils import (AverageTimer, VideoStreamer,
                          make_matching_plot_fast, frame2tensor)

torch.set_grad_enabled(False)


def match_image(): 
    center = None
    input = '../assets/map/'
    output_dir = "../results"
    image_glob = ['*.png', '*.jpg', '*.jpeg', '*.JPG']
    skip = 1
    max_length = 1000000


    # Important parameters to modify if you wish to improve the feature matching performance. 
    resize = [800] # Resize the image to this size before processing. Set to None to disable resizing.
    superglue = 'outdoor' # The SuperGlue model to use. Either 'indoor' or 'outdoor'.
    max_keypoints = -1 # -1 keep all keypoints  
    keypoint_threshold = 0.01 # Remove keypoints with low confidence. Set to -1 to keep all keypoints.
    nms_radius = 4 # Non-maxima suppression: keypoints with similar responses in a small neighborhood are removed.
    sinkhorn_iterations = 20 # Number of Sinkhorn iterations for matching.
    match_threshold = 0.5 # Remove matches with low confidence. Set to -1 to keep all matches.
    show_keypoints = True # Show the detected keypoints.
    no_display = True
    
   
    if len(resize) == 2 and resize[1] == -1:
        resize = resize[0:1]
    if len(resize) == 2:
        print('Will resize to {}x{} (WxH)'.format(
            resize[0], resize[1]))
    elif len(resize) == 1 and resize[0] > 0:
        print('Will resize max dimension to {}'.format(resize[0]))
    elif len(resize) == 1:
        print('Will not resize images')
    else:
        raise ValueError('Cannot specify more than two integers for --resize')

    device = 'cuda'
    print('Running inference on device \"{}\"'.format(device))
    config = {
        'superpoint': {
            'nms_radius': nms_radius,
            'keypoint_threshold': keypoint_threshold,
            'max_keypoints': max_keypoints
        },
        'superglue': {
            'weights': superglue,
            'sinkhorn_iterations': sinkhorn_iterations,
            'match_threshold': match_threshold,
        }
    }
    matching = Matching(config).eval().to(device)
    keys = ['keypoints', 'scores', 'descriptors']

    vs = VideoStreamer(input, resize, skip,
                       image_glob, max_length)
    frame, ret = vs.next_frame()
    assert ret, 'Error when reading the first frame (try different --input?)'

    frame_tensor = frame2tensor(frame, device)
    last_data = matching.superpoint({'image': frame_tensor})
    last_data = {k+'0': last_data[k] for k in keys}
    last_data['image0'] = frame_tensor
    last_frame = frame
    last_image_id = 0

    if output_dir is not None:
        print('==> Will write outputs to {}'.format(output_dir))
        Path(output_dir).mkdir(exist_ok=True)

    # Create a window to display the demo.
    if not no_display:
        cv2.namedWindow('SuperGlue matches', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('SuperGlue matches', 640*2*2, 480*2)
    else:
        print('Skipping visualization, will not show a GUI.')

    # Print the keyboard help menu.
    print('==> Keyboard control:\n'
          '\tn: select the current frame as the anchor\n'
          '\te/r: increase/decrease the keypoint confidence threshold\n'
          '\td/f: increase/decrease the match filtering threshold\n'
          '\tk: toggle the visualization of keypoints\n'
          '\tq: quit')

    timer = AverageTimer()

    satellite_map_index = None
    index = 0
    max_matches = -1 
    MATCHED = False
    located_image = cv2.imread("/home/marius/Desktop/Thesis_gl_hf/Wild_Nav_Master_Thesis/photos/google_earth_cover.png")
    features_mean = [0,0] #mean values of feature point coordinates
    query_image = located_image
    feature_number = 0

    while True:
        
        #current sattelite image to be matched
        frame, ret = vs.next_frame()
        if not ret:
            print('Finished demo_superglue.py')
            break
        timer.update('data')
        stem0, stem1 = last_image_id, vs.i - 1


        

        frame_tensor = frame2tensor(frame, device)
        pred = matching({**last_data, 'image1': frame_tensor})
        kpts0 = last_data['keypoints0'][0].cpu().numpy()
        kpts1 = pred['keypoints1'][0].cpu().numpy()
        matches = pred['matches0'][0].cpu().numpy()
        confidence = pred['matching_scores0'][0].cpu().numpy()
        timer.update('forward')

        valid = matches > -1
        mkpts0 = kpts0[valid]
        mkpts1 = kpts1[matches[valid]]

        """
        Find image in sattelite map with findHomography
        ******************************************
        """
        #At least 4 matched features are needed to compute homography
        MATCHED = False
        #located_image = last_frame
        print("Number of matches:", len(mkpts1))
        if (len(mkpts1) >= 4): 
            perspective_tranform_error = False           
            M, mask = cv2.findHomography(mkpts0, mkpts1, cv2.RANSAC,5.0)
            print("valid features:", mkpts1)
            query_image = last_frame
            #cv2.imshow("features", last_frame)
            #cv2.waitKey()
            #cv2.destroyAllWindows()
            matchesMask = mask.ravel().tolist()
            h,w = last_frame.shape
            #h = 400
            #w = 500
            print('Frame shape: ',last_frame.shape)
            cv2.waitKey()
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            print("Points for perspective transform: ", pts)
            try: 
                dst = cv2.perspectiveTransform(pts,M)
            except:
                print("Perspective transform error")
                perspective_tranform_error = True    
            
            cv2.waitKey()
            if (len(mkpts1) > max_matches) and not perspective_tranform_error:   
                print("Rectangle ", dst)
                frame = cv2.polylines(frame,[np.int32(dst)],True,255,3, cv2.LINE_AA) 
                moments = cv2.moments(dst)
                cX = int(moments["m10"] / moments["m00"])
                cY = int(moments["m01"] / moments["m00"])
                center = (cX  ,cY) #shape[0] is Y coord, shape[1] is X coord
                #use ratio here instead of pixels because image is reshaped in superglue
                features_mean = np.mean(mkpts0, axis = 0)
                print("Features mean: ", features_mean)
                print("Center: ", center)
                print(frame.shape[0], frame.shape[1])
                cv2.circle(frame, center, radius = 10, color = (255, 0, 255), thickness = 5)
                cv2.circle(last_frame, (int(features_mean[0]), int(features_mean[1])), radius = 10, color = (255, 0, 0), thickness = 2)
                center = (cX / frame.shape[1] ,cY /frame.shape[0] )
                # cv2.imshow("map", frame)
                # cv2.waitKey()
                satellite_map_index = index
                max_matches = len(mkpts1)
                MATCHED = True

        else:
            print("Photos were NOT matched")
      
        color = cm.jet(confidence[valid])
        text = [
            'SuperGlue',
            'Keypoints: {}:{}'.format(len(kpts0), len(kpts1)),
            'Matches: {}'.format(len(mkpts0))
        ]
        k_thresh = matching.superpoint.config['keypoint_threshold']
        m_thresh = matching.superglue.config['match_threshold']
        small_text = [
            'Keypoint Threshold: {:.4f}'.format(k_thresh),
            'Match Threshold: {:.2f}'.format(m_thresh),
            'Image Pair: {:06}:{:06}'.format(stem0, stem1),
        ]

        cv2.imwrite("Frame.jpg", frame)
        cv2.imwrite("Last_Frame.jpg", last_frame)
        out = make_matching_plot_fast(
            last_frame, frame, kpts0, kpts1, mkpts0, mkpts1, color, text='',
            path=None, show_keypoints=show_keypoints, small_text='')

        if MATCHED == True:
            located_image = out
            cv2.imwrite("located_image.png", located_image)
        

        if not no_display:
            cv2.imshow('SuperGlue matches', out)
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                vs.cleanup()
                print('Exiting (via q) demo_superglue.py')
                break
            elif key == 'n':  # set the current frame as anchor
                last_data = {k+'0': pred[k+'1'] for k in keys}
                last_data['image0'] = frame_tensor
                last_frame = frame
                last_image_id = (vs.i - 1)
            elif key in ['e', 'r']:
                # Increase/decrease keypoint threshold by 10% each keypress.
                d = 0.1 * (-1 if key == 'e' else 1)
                matching.superpoint.config['keypoint_threshold'] = min(max(
                    0.0001, matching.superpoint.config['keypoint_threshold']*(1+d)), 1)
                print('\nChanged the keypoint threshold to {:.4f}'.format(
                    matching.superpoint.config['keypoint_threshold']))
            elif key in ['d', 'f']:
                # Increase/decrease match threshold by 0.05 each keypress.
                d = 0.05 * (-1 if key == 'd' else 1)
                matching.superglue.config['match_threshold'] = min(max(
                    0.05, matching.superglue.config['match_threshold']+d), .95)
                print('\nChanged the match threshold to {:.2f}'.format(
                    matching.superglue.config['match_threshold']))
            elif key == 'k':
                show_keypoints = not show_keypoints

        timer.update('viz')
        timer.print()
        print("Index: ", index)
        #cv2.waitKey()    
        index += 1  

        if output_dir is not None:
            #stem = 'matches_{:06}_{:06}'.format(last_image_id, vs.i-1)
            stem = 'matches_{:06}_{:06}'.format(stem0, stem1)
            out_file = str(Path(output_dir, stem + '.png'))
            print('\nWriting image to {}'.format(out_file))
            cv2.imwrite(out_file, out)


    cv2.destroyAllWindows()
    vs.cleanup()
    
    return satellite_map_index, center, located_image, features_mean, last_frame, max_matches
    

