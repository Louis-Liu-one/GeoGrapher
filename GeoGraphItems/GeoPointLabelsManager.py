'''GeoGrapher点图元标签管理器
'''

__all__ = ['GeoPointLabelsManager']


class GeoPointLabelsManager:
    '''点图元标签管理类。
    '''

    def __init__(self):
        '''初始化标签管理器。
        标签管理器存储于场景对象中，一个场景只有一个标签管理器。
        '''
        self._labels = set()  # 已知标签集

    def __next__(self):
        '''获取下一个点图元标签。
        返回的标签保证不与已知标签集中的标签（`self._labels`）重复，
        且不会被自动添加到已知标签集中。

        标签从`A'开始，一直到`Z'；`Z'之后是`A_1'、`B_1'、……以此类推。
        函数按以上规则从`A'开始枚举标签，
        直到某个标签不与已知标签集中的标签重复。
        '''
        label = 'A'
        letterAt = numberAt = 0
        while label in self._labels:  # 保证不重复
            letterAt += 1
            if letterAt == 26:
                letterAt = 0
                numberAt += 1
            label = chr(65 + letterAt) + (  # 生成下一个标签
                '_' + str(numberAt) if numberAt else '')
        return label

    def addLabel(self, label):
        '''向已知标签集中添加标签，返回是否成功。
        若添加的标签不在已知标签集中，则成功。
        '''
        if label not in self._labels:
            self._labels.add(label)
            return True
        return False

    def setLabel(self, raw, label):
        '''将已知标签集中的`raw`标签修改为`label`标签，返回是否成功。
        若`raw`标签在已知标签集中，
        且`label`标签不在已知标签集中或与`raw`相同，则成功。
        '''
        if raw in self._labels and (
                label not in self._labels or label == raw):
            self._labels.remove(raw)
            self._labels.add(label)
            return True
        return False

    def removeLabel(self, label):
        '''删除已知标签集中的标签，返回是否成功。
        若删除的标签在已知标签集中，则成功。
        '''
        if label in self._labels:
            self._labels.remove(label)
            return True
        return False
