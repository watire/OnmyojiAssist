from game_window import *
from game_control import *
from enum import Enum, unique
import threading


@unique
class Role(Enum):
    Unknown = 0
    Single = 1
    Driver = 2
    Passenger = 3

@unique
class WorkType(Enum):
    YuHun = 1
    JieJieKa = 2


class QuitThread(Exception):
    pass


class OnmyojiThread(threading.Thread):
    def __init__(self, onmyoji_assist, hwnd, lock):
        super(OnmyojiThread, self).__init__()
        self._stop_event = threading.Event()
        self._onmyoji_assist = onmyoji_assist
        self._hwnd = hwnd
        self._lock = lock
        self._role = Role.Unknown
        self._stop_after_finish = False
        self._count = 0
        self._work_type = WorkType.YuHun

    def set_work_type(self, work_type):
        self._work_type = work_type

    def set_count(self, count):
        self._count = count

    def set_stop_after_finish(self):
        self._stop_after_finish = True

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def run(self):
        logger.info("线程(%s) 开始运行" % self.getName())
        try:
            if self._work_type == WorkType.YuHun:
                #self.__test_loop()
                self.__role_judgement()
                self.__main_loop()
            elif self._work_type == WorkType.JieJieKa:
                self.__jiejieka_compositing_loop()
        except QuitThread:
            logger.info("线程(%s) 已退出" % self.getName())

    def __jiejieka_compositing_loop(self):
        logger.info("线程(%s) 开始合成结界卡" % self.getName())
        counter = 0
        while not self.is_stopped():
            counter += 1
            self.__jiejieka_compositing()
            self.__sleep_or_quit(2000, 1000)
            self.__check_jiejieka_compositing_result(counter)
            self.__sleep_or_quit(500)
            self.__add_jiejieka()
            self.__sleep_or_quit(500, 1500)

    def __check_jiejieka(self):
        pos = (IMG_JIE_JIE_KA_YUAN_LIAO[0], IMG_JIE_JIE_KA_YUAN_LIAO[1])
        pos_end = (IMG_JIE_JIE_KA_YUAN_LIAO[2], IMG_JIE_JIE_KA_YUAN_LIAO[3])
        index = self.__check_image_type(pos, pos_end, './img/JIEJIEKA_ADD_EMPTY1.bmp', './img/JIEJIEKA_ADD_EMPTY2.bmp',
                                        './img/JIEJIEKA_ADD_EMPTY3.bmp')
        empty = True if index == 0 or index == 1 or index == 2 else False
        if empty:
            logger.info("线程(%s) 合成原料空缺,停止合成" % self.getName())
            self.__emit_stop_signal()
        else:
            return True

    def __jiejieka_compositing(self):
        pos_start = (IMG_HE_CHENG_JIE_JIE_KA[0], IMG_HE_CHENG_JIE_JIE_KA[1])
        pos_end = (IMG_HE_CHENG_JIE_JIE_KA[2], IMG_HE_CHENG_JIE_JIE_KA[3])
        with self._lock:
            max_val, pos = find_image(self._hwnd, './img/JIEJIEKA_START_COMPOSITING.bmp', pos_start, pos_end)
        if max_val > 0.9:
            if self.__check_jiejieka():
                logger.debug("线程(%s) 开始合成" % (self.getName()))
                click(self._hwnd, (pos_start[0] + pos[0], pos_start[1] + pos[1]),
                      (pos_start[0] + pos[2], pos_start[1] + pos[3]))
        else:
            logger.info("线程(%s) 无法识别合成界面" % self.getName())
            self.__emit_stop_signal()

    def __check_jiejieka_compositing_result(self, counter):
        pos_start = (IMG_XIN_JIE_JIE_KA[0], IMG_XIN_JIE_JIE_KA[1])
        pos_end = (IMG_XIN_JIE_JIE_KA[2], IMG_XIN_JIE_JIE_KA[3])
        index = self.__check_image_type(pos_start, pos_end, './img/JIE_JIE_KA_DOU_YU.bmp', './img/JIE_JIE_KA_SAN_SHI_NEI.bmp',
                                        './img/JIE_JIE_KA_TAI_GU.bmp', './img/JIE_JIE_KA_TAI_YIN.bmp')
        if index == 0:
            logger.info("线程(%s) 第%d次合成：斗鱼" % (self.getName(), counter))
        elif index == 1:
            logger.info("线程(%s) 第%d次合成：伞室内" % (self.getName(), counter))
        elif index == 2:
            logger.info("线程(%s) 第%d次合成：太鼓" % (self.getName(), counter))
        elif index == 3:
            logger.info("线程(%s) 第%d次合成：太阴" % (self.getName(), counter))
        else:
            logger.info("线程(%s) 第%d次合成：无法识别" % (self.getName(), counter))
        if self._count == counter:
            logger.info("线程(%s) 合成结界卡%d次，完成合成" % (self.getName(), counter))
            self.__emit_stop_signal()

    def __add_jiejieka(self):
        pos_start = (IMG_TIAN_JIA_JIE_JIE_KA[0], IMG_TIAN_JIA_JIE_JIE_KA[1])
        pos_end = (IMG_TIAN_JIA_JIE_JIE_KA[2], IMG_TIAN_JIA_JIE_JIE_KA[3])
        with self._lock:
            max_val, pos = find_image(self._hwnd, './img/JIEJIEKA_CONTINUE_ADD.bmp', pos_start, pos_end)
        if max_val > 0.9:
            logger.debug("线程(%s) 继续添加结界卡" % self.getName())
            click(self._hwnd, (pos_start[0] + pos[0], pos_start[1] + pos[1]),
                  (pos_start[0] + pos[2], pos_start[1] + pos[3]))

    def __test_loop(self):
        counter = 0
        while not self.is_stopped():
            counter += 1
            logger.info('Thread(%s) count %d' % (self.getName(), counter))
            self.__sleep_or_quit(500, 2000)
            logger.debug('Thread(%s) count %d  1' % (self.getName(), counter))
            self.__check_counter(counter)
            self.__sleep_or_quit(1000)
            logger.debug('Thread(%s) count %d  2' % (self.getName(), counter))
            self.__sleep_or_quit(1000)
            logger.debug('Thread(%s) count %d  3' % (self.getName(), counter))

    def __emit_stop_signal(self):
        self.stop()
        self._onmyoji_assist.stop_signal.emit(int(self.getName()))

    def __sleep_or_quit(self, sleep_time, variable_time=0):
        if not self.is_stopped():
            random_sleep(sleep_time, variable_time)
        if self.is_stopped():
            logger.debug("线程(%s) 即将停止" % self.getName())
            if self._work_type == WorkType.YuHun:
                self.__close_yu_hun_buff()
            raise QuitThread('quit')

    def __role_judgement(self):
        self._role = Role.Unknown
        start_time = time.clock()
        while self._role == Role.Unknown:
            self.__sleep_or_quit(500)
            self.__reject_reward()
            with self._lock:
                is_xie_zhan, _ = find_image(self._hwnd, './img/XIE_ZHAN_DUI_WU.bmp')
                is_tiao_zhan, _ = find_image(self._hwnd, './img/TIAO_ZHAN_READY.bmp')
            if is_xie_zhan > 0.9 and is_tiao_zhan > 0.9:
                self._role = Role.Driver
            elif is_xie_zhan > 0.9:
                self._role = Role.Passenger

            current_time = time.clock()
            if current_time - start_time > 10:
                logger.error("线程(%s) 10s 内无法识别角色，正在退出" % self.getName())
                self.__emit_stop_signal()

    def __main_loop(self):
        logger.info("线程(%s) 主循环开始，识别出角色：%s" % (self.getName(), str(self._role)))
        counter = 0
        while not self.is_stopped():
            counter += 1
            self.__enter_battlefield()

            # 检测是否进入战场
            while True:
                entered, index = self.__wait_till_multi_image('./img/ZHUN_BEI.bmp', './img/ZI_DONG.bmp', max_time=60)
                if not entered:
                    logger.error("线程(%s) 未能进入战场，正在退出" % self.getName())
                    self.__emit_stop_signal()
                elif index == 0:
                    if not self.__click_till_image('./img/ZHUN_BEI.bmp', (994, 458), (1081, 522), 10, True):
                        logger.error("线程(%s) 无法完成准备，正在退出" % self.getName())
                        self.__emit_stop_signal()
                    logger.debug("线程(%s) 已准备" % self.getName())
                    continue
                elif index == 1:
                    logger.debug("线程(%s) 已开始战斗" % self.getName())
                    break

            # 等待战斗结束
            if not self.__wait_till_image('./img/ZI_DONG.bmp', 600, True):
                logger.error("线程(%s) 仍未结束战斗，正在退出" % self.getName())
                self.__emit_stop_signal()
            logger.debug("线程(%s) 结束战斗" % self.getName())

            # 检测战斗结果
            finished, index = self.__wait_till_multi_image('./img/SHENG_LI.bmp', './img/SHI_BAI.bmp', max_time=60)
            if not finished:
                logger.error("线程(%s) 未能进入战场，正在退出" % self.getName())
            victory = True if index == 0 else False
            self.__bonus_received(victory)
            self.__check_yuhun_overflow(victory)
            self.__check_counter(counter)
            self.__sleep_or_quit(1000, 500)
            logger.debug("线程(%s) 准备进入下一轮" % self.getName())
            self.__regroup_team(victory)

    def __enter_battlefield(self):
        if self._role == Role.Single:
            self.__emit_stop_signal()
            pass
            # while not self.__is_color_single():
            #     self.__reject_xuan_shang()
            #     self.__sleep_or_quit(500)
            # click_in_region(self._ts, *Region_TiaoZhan_Single)
        elif self._role == Role.Driver:
            while True:
                self.__sleep_or_quit(800)
                self.__reject_reward()
                with self._lock:
                    waiting, _ = find_image(self._hwnd, './img/TIAO_ZHAN_WAITING.bmp')
                    ready, _ = find_image(self._hwnd, './img/TIAO_ZHAN_READY.bmp')
                if waiting > ready > 0.9:
                    logger.debug("线程(%s) 等待队友加入" % self.getName())
                elif ready > waiting > 0.9:
                    pos_lt = (POS_TEAM_TIAO_ZHAN[0], POS_TEAM_TIAO_ZHAN[1])
                    pos_rb = (POS_TEAM_TIAO_ZHAN[2], POS_TEAM_TIAO_ZHAN[3])
                    click(self._hwnd, pos_lt, pos_rb)
                    break
        elif self._role == Role.Passenger:
            pass
        logger.debug("线程(%s) 正在进入战场" % self.getName())

    def __check_yuhun_overflow(self, win=True):
        if win is not True:
            return
        self.__reject_reward()
        with self._lock:
            overflow, _ = find_image(self._hwnd, './img/OVERFLOW.bmp')
        if overflow < 0.9:
            return
        if not self.__click_till_image('./img/OVERFLOW.bmp', POS_OVERFLOW_OK_LT, POS_OVERFLOW_OK_RB, 10, False):
            logger.error("线程(%s) 不能离开御魂溢出界面，正在退出" % self.getName())

    def __bonus_received(self, win=None):
        result = "胜利" if win else "失败！！"
        logger.debug("线程(%s) 战斗结束：%s" % (self.getName(), result))
        if self._role == Role.Single:
            pass
        elif self._role == Role.Driver or self._role == Role.Passenger:
            if win:
                if not self.__click_till_image('./img/JIE_SUAN.bmp', (937, 484), (1077, 547), 30):
                    logger.error("线程(%s) 不能进入奖励界面，正在退出" % self.getName())
                    self.__emit_stop_signal()
                    return
                if not self.__click_till_image('./img/JIE_SUAN.bmp', (937, 484), (1077, 547), 30, True):
                    logger.error("线程(%s) 不能离开奖励界面，正在退出" % self.getName())
                    self.__emit_stop_signal()
                    return
            elif self._role == Role.Passenger:
                if not self.__click_till_image('./img/SHI_BAI.bmp', (937, 484), (1077, 547), 30, True):
                    logger.error("线程(%s) 不能离开失败界面，正在退出" % self.getName())
            elif self._role == Role.Driver:
                if not self.__click_till_image('./img/JI_XU.bmp', (937, 484), (1077, 547), 30):
                    logger.error("线程(%s) 不能离开失败界面，正在退出" % self.getName())
                    self.__emit_stop_signal()
                    return

    def __regroup_team(self, win=None):
        if self._role == Role.Single:
            pass
        elif self._role == Role.Driver:
            self.__reject_reward()
            with self._lock:
                invite, _ = find_image(self._hwnd, './img/JI_XU.bmp')
            if invite > 0.9:
                logger.debug("线程(%s) 自动邀请队友" % self.getName())
                if win:
                    click(self._hwnd, (490, 310), (505, 327))
                    self.__sleep_or_quit(500, 500)
                click(self._hwnd, (600, 360), (747, 405))
            self.__sleep_or_quit(500)
            if not self.__wait_till_image('./img/XIE_ZHAN_DUI_WU.bmp', 60):
                logger.error("线程(%s) 不能进入组队界面，正在退出" % self.getName())
                self.__emit_stop_signal()
        elif self._role == Role.Passenger:
            while True:
                self.__reject_reward()
                with self._lock:
                    if win:
                        invitation, pos = find_image(self._hwnd, './img/INVITATION.bmp')
                    else:
                        invitation, pos = find_image(self._hwnd, './img/INVITATION_2.bmp')
                    in_team, _ = find_image(self._hwnd, './img/XIE_ZHAN_DUI_WU.bmp')
                if invitation > 0.9:
                    logger.debug("线程(%s) 自动接收组队邀请" % self.getName())
                    click(self._hwnd, (pos[0]+20, pos[1]+20), (pos[0]+50, pos[1]+50))
                    break
                elif in_team > 0.9:
                    break
                self.__sleep_or_quit(500)

    def __check_counter(self, counter):
        logger.info("<--- 线程(%s) 第 %d 次战斗结束 --->" % (self.getName(), counter))
        if self._count == counter or self._stop_after_finish:
            logger.info("<--- 线程(%s) 计划任务 %d/%d 完成 --->" % (self.getName(), counter, self._count))
            self.__emit_stop_signal()

    def __close_yu_hun_buff(self):
        logger.debug("<--- 线程(%s) 检测御魂加成 --->" % (self.getName()))
        pos_start = (IMG_JIA_CHENG[0], IMG_JIA_CHENG[1])
        pos_end = (IMG_JIA_CHENG[2], IMG_JIA_CHENG[3])
        random_sleep(1000, 2000)
        with self._lock:
            max_val, pos = find_image(self._hwnd, './img/JIA_CHENG.bmp', pos_start, pos_end)
        logger.debug("线程(%s) 查找加成入口 匹配度：%f" % (self.getName(), max_val))
        if max_val > 0.9:
            logger.debug("线程(%s) 找到加成入口" % self.getName())
            click(self._hwnd, (pos_start[0] + pos[0], pos_start[1] + pos[1]),
                  (pos_start[0] + pos[2], pos_start[1] + pos[3]))
            pos_start_yu_hun = (IMG_JIA_CHENG_YU_HUN[0], IMG_JIA_CHENG_YU_HUN[1])
            pos_end_yu_hun = (IMG_JIA_CHENG_YU_HUN[2], IMG_JIA_CHENG_YU_HUN[3])
            random_sleep(1000, 2000)
            with self._lock:
                buff_yu_hun_on, _ = find_image(self._hwnd, './img/JIA_CHENG_YU_HUN_KAI.bmp', pos_start_yu_hun, pos_end_yu_hun)
            with self._lock:
                buff_yu_hun_off, _ = find_image(self._hwnd, './img/JIA_CHENG_YU_HUN_GUAN.bmp', pos_start_yu_hun, pos_end_yu_hun)
            logger.debug("线程(%s) 找到御魂加成 开：%f 关：%f" % (self.getName(), buff_yu_hun_on, buff_yu_hun_off))
            if buff_yu_hun_on > buff_yu_hun_off > 0.9:
                click(self._hwnd, (POS_JIA_CHENG_YU_HUN[0], POS_JIA_CHENG_YU_HUN[1]), (POS_JIA_CHENG_YU_HUN[2], POS_JIA_CHENG_YU_HUN[3]))
                logger.info("<--- 线程(%s) 关闭御魂加成 --->" % self.getName())
            else:
                logger.info("<--- 线程(%s) 御魂加成是关闭状态 --->" % self.getName())
            click(self._hwnd, (pos_start[0] + pos[0], pos_start[1] + pos[1]), (pos_start[0] + pos[2], pos_start[1] + pos[3]))
        else:
            logger.debug("线程(%s) 未找到加成入口：%d" % (self.getName(), max_val))

    def __reject_reward(self):
        pos = (IMG_XUAN_SHANG[0], IMG_XUAN_SHANG[1])
        pos_end = (IMG_XUAN_SHANG[2], IMG_XUAN_SHANG[3])
        with self._lock:
            max_val, _ = find_image(self._hwnd, './img/XUAN_SHANG.bmp', pos, pos_end)
        if max_val > 0.9:
            logger.info("线程(%s) 检测到悬赏邀请" % self.getName())
            index = self.__check_reward_type('./img/GOU_YU.bmp', './img/TI_LI.bmp')
            can_accept = True if index == 0 else False
            self.__sleep_or_quit(650, 250)
            if can_accept:
                pos = (POS_ACCEPT_XUAN_SHANG[0], POS_ACCEPT_XUAN_SHANG[1])
                pos_end = (POS_ACCEPT_XUAN_SHANG[2], POS_ACCEPT_XUAN_SHANG[3])
                logger.info("线程(%s) 已接受悬赏" % self.getName())
            else:
                pos = (POS_REJECT_XUAN_SHANG[0], POS_REJECT_XUAN_SHANG[1])
                pos_end = (POS_REJECT_XUAN_SHANG[2], POS_REJECT_XUAN_SHANG[3])
                logger.info("线程(%s) 已拒绝悬赏" % self.getName())
            click(self._hwnd, pos, pos_end)
        self.__sleep_or_quit(50)

    def __check_image_type(self, pos, pos_end, *image_paths):
        for index, image in enumerate(image_paths):
            with self._lock:
                max_val, _ = find_image(self._hwnd, image, pos, pos_end)
            if max_val > 0.9:
                return index
        return -1

    def __check_reward_type(self, *image_paths):
        for index, image in enumerate(image_paths):
            with self._lock:
                max_val, _ = find_image(self._hwnd, image)
            if max_val > 0.9:
                return index
        return -1

    def __wait_till_image(self, image_path, max_time=0, disappear=False):
        start_time = time.clock()
        while True:
            self.__sleep_or_quit(1000)
            self.__reject_reward()
            if time.clock() - start_time > max_time > 0:
                return False
            with self._lock:
                max_val, _ = find_image(self._hwnd, image_path)
            if (max_val > 0.9) is not disappear:
                return True

    def __wait_till_multi_image(self, *image_paths, max_time=0):
        start_time = time.clock()
        while True:
            self.__sleep_or_quit(1000)
            self.__reject_reward()
            if time.clock() - start_time > max_time > 0:
                return False, None
            for index, image in enumerate(image_paths):
                with self._lock:
                    max_val, _ = find_image(self._hwnd, image)
                if max_val > 0.9:
                    return True, index

    def __click_till_image(self, image_path, click_pos_lt, click_pos_rb, max_time=0, disappear=False):
        start_time = time.clock()
        while True:
            self.__sleep_or_quit(300, 300)
            self.__reject_reward()
            if time.clock() - start_time > max_time > 0:
                return False
            with self._lock:
                max_val, _ = find_image(self._hwnd, image_path)
            if (max_val > 0.9) is not disappear:
                return True
            else:
                click(self._hwnd, click_pos_lt, click_pos_rb)
