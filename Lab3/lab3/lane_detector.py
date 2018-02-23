import cv2
import numpy as np
#import matplotlib.pyplot as plt

class LaneDetector:
    def compute_binary_image(self, color_image, plot=False):    
        # Convert to HLS color space and separate the S channel
        # Note: img is the undistorted image
        hls = cv2.cvtColor(color_image, cv2.COLOR_RGB2HLS)
        s_channel = hls[:,:,2]

        # Grayscale image
        # NOTE: we already saw that standard grayscaling lost color information for the lane lines
        # Explore gradients in other colors spaces / color channels to see what might work better
        gray = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)

        # Sobel x
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0) # Take the derivative in x
        abs_sobelx = np.absolute(sobelx) # Absolute x derivative to accentuate lines away from horizontal
        scaled_sobel = np.uint8(255*abs_sobelx/np.max(abs_sobelx))

        # Threshold x gradient
        thresh_min = 20
        thresh_max = 100
        sxbinary = np.zeros_like(scaled_sobel)
        sxbinary[(scaled_sobel >= thresh_min) & (scaled_sobel <= thresh_max)] = 1

        # Threshold color channel
        #s_thresh_min = 170
        #s_thresh_max = 255
        #s_binary = np.zeros_like(s_channel)
        #s_binary[(s_channel >= s_thresh_min) & (s_channel <= s_thresh_max)] = 1

        # Combine the two binary thresholds
        #combined_binary = np.zeros_like(sxbinary)
        #combined_binary[(s_binary == 1) | (sxbinary == 1)] = 1

        b_binary = np.zeros_like(gray)
        b_binary[(gray >= 160)] = 1
        combined_binary = np.zeros_like(sxbinary)
        combined_binary[(b_binary == 1) | (sxbinary == 1)] = 1

        kernel = np.ones((5,5), np.uint8)
        final = combined_binary
        final = cv2.erode(final, kernel, iterations=1)
        final = cv2.dilate(final, kernel, iterations=1)
        final = cv2.erode(final, kernel, iterations=1)
        final = cv2.dilate(final, kernel, iterations=1)

        if (plot):
            # Ploting both images Original and Binary
            f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
            ax1.set_title('Undistorted/Color')
            ax1.imshow(color_image)    
            ax2.set_title('Binary/Combined S channel and gradient thresholds')
            ax2.imshow(combined_binary, cmap='gray')
            plt.show()

        return final

    def compute_perspective_transform(self, binary_image):
        # Define 4 source and 4 destination points = np.float32([[,],[,],[,],[,]])
        shape = binary_image.shape[::-1] # (width,height)
        w = shape[0]
        h = shape[1]
        transform_src = np.float32([ [206 / 1.6,569 / 1.6], [0,h], [1020 / 1.6,h], [802 / 1.6,558 / 1.6]])
        transform_dst = np.float32([ [0,0], [0,h], [w,h], [w,0]])
        M = cv2.getPerspectiveTransform(transform_src, transform_dst)
        return M

    def apply_perspective_transform(self, binary_image, M, plot=False):
        warped_image = cv2.warpPerspective(binary_image, M, (binary_image.shape[1], binary_image.shape[0]), flags=cv2.INTER_NEAREST)  # keep same size as input image
        if(plot):
            # Ploting both images Binary and Warped
            f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
            ax1.set_title('Binary/Undistorted and Tresholded')
            ax1.imshow(binary_image, cmap='gray')
            ax2.set_title('Binary/Undistorted and Warped Image')
            ax2.imshow(warped_image, cmap='gray')
            plt.show()

        return warped_image

    def extract_lanes_pixels(self, binary_warped):

        # Take a histogram of the bottom half of the image
        histogram = np.sum(binary_warped[binary_warped.shape[0]/2:,:], axis=0)
        #plt.plot(histogram)
        #plt.show()
        # Create an output image to draw on and  visualize the result
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
        # Find the peak of the left and right halves of the histogram
        # These will be the starting point for the left and right lines
        midpoint = np.int(histogram.shape[0]/2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        # Choose the number of sliding windows
        nwindows = 9
        # Set height of windows
        window_height = np.int(binary_warped.shape[0]/nwindows)
        # Identify the x and y positions of all nonzero pixels in the image
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        # Current positions to be updated for each window
        leftx_current = leftx_base
        rightx_current = rightx_base
        # Set the width of the windows +/- margin
        margin = 100
        # Set minimum number of pixels found to recenter window
        minpix = 50
        # Create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = binary_warped.shape[0] - (window+1)*window_height
            win_y_high = binary_warped.shape[0] - window*window_height
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # Draw the windows on the visualization image
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2)
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2)
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        # Extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        return leftx, lefty, rightx, righty, left_lane_inds, right_lane_inds

    def poly_fit(self, leftx, lefty, rightx, righty, left_lane_inds, right_lane_inds, binary_warped, plot=False):

        # Fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        # Generate x and y values for plotting
        ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

        # Identify the x and y positions of all nonzero pixels in the image
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
        out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
        out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

        if(plot):
            plt.imshow(out_img)
            plt.plot(left_fitx, ploty, color='yellow')
            plt.plot(right_fitx, ploty, color='yellow')
            plt.xlim(0, 1280)
            plt.ylim(720, 0)
            plt.show()

        if(True):
            p = binary_warped

        return left_fit, right_fit, ploty, left_fitx, right_fitx

    def detect(self, color_img):
        plot = False

        binary_img = self.compute_binary_image(color_img, plot)

        #m = self.compute_perspective_transform(binary_img)
        #img = self.apply_perspective_transform(binary_img, m, plot)

        shape = binary_img.shape # (width,height)
        w = shape[1]
        h = shape[0]
        img = binary_img[int(h * 2/ 3.):]

        if plot:
            histogram = np.sum(img, axis=0)
            plt.plot(histogram)
            plt.show()

        leftx, lefty, rightx, righty, left_lane_inds, right_lane_inds = self.extract_lanes_pixels(img)
        left_fit, right_fit, ploty, left_fitx, right_fitx = self.poly_fit(leftx, lefty, rightx, righty, left_lane_inds, right_lane_inds, img, plot)

        mid_x = (left_fitx[-1] + right_fitx[-1]) / 2

        return mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx 

if __name__ == "__main__":
    color_img = cv2.imread("frame.png")

    detector = LaneDetector()
    print detector.detect(color_img)

