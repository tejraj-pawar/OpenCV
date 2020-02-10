import cv2,time, pandas, datetime, imutils, smtplib

# to store initial frame
first_frame = None
# it will start capturing the video from live webcam
video = cv2.VideoCapture(0)

status_list = [None, None]
times = []
df = pandas.DataFrame(columns = ['Object Appeared', 'Object Disappeared'])
sendNotification = 1
emailId = 'pawartejraj47@gmail.com'

# notify admin when there is change in frame for thr first time
def notify_admin(time):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # Next, log in to the server
    server.login("pawartejraj47@gmail.com", "*******")

    # Send the mail
    msg = "Alert!!!!!! /n First Object appeared at: {}".format(time) # The /n separates the message from the headers
    server.sendmail("pawartejraj47@gmail.com", "pawartejraj47@gmail.com", msg)
    print("Email Sent!!")

while True:
    # here 'check' will return true if opencv is able to read video file and
    # 'frame' is a numpy array, it represents first image that video captures.
    check, frame = video.read()

    # status is zero as initially object/motion is not visible.
    status = 0

    # convert a frame to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # convert the gray scale frame to GuassianBlur
    gray = cv2.GaussianBlur(gray, (21,21),0)

    if first_frame is None:
        first_frame = gray
        continue

    # it cal. the diff. between first and other frames
    delta_frame = cv2.absdiff(first_frame, gray)

    # here we are setting threshold as 30 and max value as 255. i.e. it diff. is < 30 then it will convert that pixel to black else white.
    thresh_delta = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_delta = cv2.dilate(thresh_delta, None, iterations=0)


    # define the contour area. basically add the borders.
    cnts = cv2.findContours(thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for contour in cnts:
        # romove noises and shadows. i.e. it'll keep only that part white, which has area greater than 1000 pixels
        if cv2.contourArea(contour) < 1000:
            continue
        # as object appears status will become 1
        status = 1
        # it will create rectangular boxes aroud objects in the frame
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)

        #notify admin when there is change in frame for thr first time
        if(sendNotification == 1):
            #notify_admin(datetime.datetime.now())
            sendNotification = 0

    # to record time when object appears and disappears.
    status_list.append(status)      # add status to the list
    status_list = status_list[-2:] # take last two element from list

    # below condition makes sure that in 2nd last image(previous) there was no object but in last image(recent) there is object (i.e. new onject appeared)
    if status_list[-1] == 1 and status_list[-2] == 0:
        print("New Object appreared: {}",format(datetime.datetime.now()))
        times.append(datetime.datetime.now())
    # below condition makes sure that in 2nd last image(previous) there was object but in last image(recent) that object disappeared (i.e. object desappeared)
    if status_list[-1] == 0 and status_list[-2] == 1:
        print("Object disappeared: {}",format(datetime.datetime.now()))
        times.append(datetime.datetime.now())

    # here we are showing all the frame
    cv2.imshow('frame', frame)  # this is the main frame
    cv2.imshow('Capturing..', gray)  # this is gray scale of main frame
    #cv2.imshow('delta_frame', delta_frame)  # this is diff. between first and current main frame
    #cv2.imshow('thresh_frame', thresh_delta)  # this is threshold frame i.e after applying threshold

    # frame will change in 1000 millisecond
    key = cv2.waitKey(1000)

    # this will break loop, once user press 'q'
    if key == ord('q'):
        break

# store object data(time at which onject appeared and disappeared) in dataframe
for i in range(0, len(times)-1, 2):
    df=df.append({'Start':times[i], 'End':times[i+1]}, ignore_index=True)

# save dataframe to csv file.
df.to_csv("Times.csv")

video.release()
cv2.destroyAllWindows()



