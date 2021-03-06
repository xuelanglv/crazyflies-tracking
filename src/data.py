from collections import deque

# 滤波权重
FILTER_POWER = (27, 20, 15, 11, 8, 6, 4, 2, 1, 1)
# 滤波权重和
FILTER_SUM = 95

class Data(object):
    # 节拍
    beat = 0

    # 原始距离信息
    raw_distance = deque([0]*100, maxlen=5000)
    # 可用的距离数据，已滤波
    distance = deque([0]*100, maxlen=5000)
    # 衡量距离在快速变化的量
    distance_rapid_changing = 0

    rapid_changing = 0

    def update(self, timestamp, _data, logconf):
        self.push_raw_distance(_data['ranging.distance0'])

        self.next_beat()

    def push_raw_distance(self, raw_distance):
        self.raw_distance.append(raw_distance)

        history = [self.raw_distance[-x] for x in range(1, 11)]
        filter_result = 0

        for i in range(10):
            filter_result += history[i] * FILTER_POWER[i]
        filter_result /= FILTER_SUM

        self.distance.append(filter_result)

    def next_beat(self):
        self.beat += 1
        self.beat = self.beat % 1024

    def distance_check(self):
        # 失联处理
        if self.raw_distance[-1] == self.raw_distance[-2] and \
            self.raw_distance[-1] == self.raw_distance[-3] and \
                self.raw_distance[-1] == self.raw_distance[-4]:
            print(self.raw_distance)
            print('失联前的数据 ↑')
            raise Exception('无人机与 anchor 失联')

        # 距离快速变化
        if self.distance[-1] > \
            0.5 + (self.distance[-2] + self.distance[-3] +
                   self.distance[-4] + self.distance[-5]) / 4:
            if self.rapid_changing >= 5:
                self.rapid_changing = 7
            else:
                self.distance[-1] = self.distance[-2]
                self.rapid_changing += 2
        else:
            if self.rapid_changing > 0:
                self.rapid_changing -= 1
