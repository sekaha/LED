
class Sprite:
    # sprite collects and points to canvases
    def __init__(self, filename="", origin_x=0, origin_y=0):
        # image index and image speed
        self.frames = []
        self.frame = 0
        self.frame_rate = 0
        self.frame_offset = 0
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.angle = 0
        self.img_scale = 1
        self.width = 0
        self.height = 0

        if filename != "":
            try:
                image = pygame.image.load(filename)
                self.origin_x, self.origin_y = origin_x, origin_y
                image = image.convert_alpha()

                self.frames.append(Canvas(0, 0, origin_x, origin_y, image))
                self.width = self.frames[0].get_width()
                self.height = self.frames[0].get_height()
            except pygame.error as e:
                print(f"Unable to load {filename}")
                raise SystemExit(e)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.get_current_frame()[key]
        else:
            return self.frames[key % len(self.frames)]

    def __setitem__(self, key, canvas):
        self.frames[key % len(self.frames)] = canvas

    def __eq__(self, other):
        return (self.get_rgb() == other.get_rgb()).all()

    def set_frame(self, frame):
        self.frame = frame

    def get_ndarray(self):
        return self.get_current_frame().get_ndarray()

    def get_frame(self):
        return math.floor(self.frame + self.frame_offset) % len(self.frames)

    def get_current_frame(self):
        return self.frames[self.get_frame()]

    def append(self, canvas):
        if (type(canvas) == Sprite) or (type(canvas) == Canvas) or (type(canvas)):
            self.frames.append(canvas)
        else:
            raise TypeError(f"cannot append non-canvas object of type {type(canvas)}")

    def center_origin(self):
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin(self, x, y):
        self.origin_x = x
        self.origin_y = y

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin_x(self, x):
        self.origin_x = x

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin_y(self, y):
        self.origin_y = y

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def get_origin_x(self):
        return self.origin_x

    def get_origin_y(self):
        return self.origin_y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def rotate(self, angle):
        self.angle = angle
        self.get_current_frame().rotate(angle)

    def get_angle(self):
        return self.angle

    def scale(self, scale):
        self.img_scale = scale

    def get_scale(self):
        return self.img_scale

    def set_frame_rate(self, frame_rate):
        if frame_rate == 0:
            # if the frame rate is now zero, don't update this sprite
            if _animated_sprites.count(self) > 0:
                _animated_sprites.remove(self)

        # if the frame rate is now more than 0 and the sprite isn't already set to be updated
        # put it in the update list
        elif _animated_sprites.count(self) < 1:
            _animated_sprites.append(self)
        self.frame_rate = frame_rate

    def get_frame_rate(self):
        return self.frame_rate

    def get_frame_count(self):
        return len(self.frames)

    def get_rgb(self):
        return pygame.surfarray.array3d(self.get_current_frame().surface)

    def get_rgba(self):
        return np.dstack((self.get_rgb(), self.get_alpha()))

    def get_red(self):
        return np.dsplit(self.get_rgb(), 3)[0]

    def get_green(self):
        return np.dsplit(self.get_rgb(), 3)[1]

    def get_blue(self):
        return np.dsplit(self.get_rgb(), 3)[2]

    def get_alpha(self):
        return pygame.surfarray.array_alpha(self.get_frame().surface)

    def trim(self, x, y, w, h):
        canvas = self.get_current_frame().surface

        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect((x, y, w, h))
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(canvas, (0, 0), rect)
        return Canvas(0, 0, 0, 0, image)