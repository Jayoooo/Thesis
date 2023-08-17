import pickle
from rf2tna import TableEntry, MATable, Tree2TNA


class DMLevelEntry(TableEntry):
    """
    The entry of Level table in Direct Mapping Method(switchtree)
    """

    def __init__(self, level, **kwargs):
        """
        kwargs:
            parent_n
            isLarge

            ====exclusive====
            class_
            -----------------
            feature
            now_n
            threshold
            =================

        """
        super().__init__()
        self.level = level

        self.field["prev_node"] = int(kwargs["parent_n"])
        self.field["isLarge"] = kwargs["isLarge"]

        if "class_" in kwargs:
            # The level entry is for SetClass

            self.field["action_name"] = "SetClass"
            self.action = "setclass"

            self.field["class_num"] = int(kwargs["class_"])

            self.print_fmt = "level_{level:<2}  {prev_node:4} {isLarge:3} => SetClass({class_num})"
        else:
            # The level entry is for CheckFeature
            self.field["action_name"] = f"CheckFeature{kwargs['feature']}"
            self.action = "checkfeature"

            self.field["now_node"] = int(kwargs["now_n"])
            self.field["threshold"] = int(kwargs["threshold"])

            self.print_fmt = "level_{level:<2}  {prev_node:4} {isLarge:3} => {action_name:7}({now_node:4}, {threshold:9})"


class DMTable(MATable):
    """
    Direct Mapping table
    """

    def __init__(self, table_name):
        super().__init__(table_name)

    def insert_rule(self, level, **kwargs):
        new_entry = DMLevelEntry(level, **kwargs)
        self.entries.append(new_entry)


class DirectMapping(Tree2TNA):
    """ Direct-Mapping Method """

    def __init__(self, decision_tree, feature_names):
        super().__init__(decision_tree, feature_names)

        dm_tables = self.generate_direct_mapping_rule()
        self.dm_count = 0
        for lv, tbl in dm_tables.items():
            self.dm_count += len(tbl.entries)

    def generate_direct_mapping_rule(self):
        self.DM_TABLES = {}

        def dfs(parent_n, now_n, isLarge, depth):
            if self.children_left[now_n] == self.children_right[now_n]:  # is leaf
                if depth not in self.DM_TABLES:
                    self.DM_TABLES[depth] = DMTable(f"level{depth}")

                self.DM_TABLES[depth].insert_rule(
                    depth, parent_n=parent_n + 1, isLarge=isLarge, class_=self.class_[now_n])

            else:
                if depth not in self.DM_TABLES:
                    self.DM_TABLES[depth] = DMTable(f"level{depth}")

                self.DM_TABLES[depth].insert_rule(
                    depth, parent_n=parent_n + 1, isLarge=isLarge, now_n=now_n + 1, threshold=self.threshold[now_n], feature=self.feature[now_n])

                dfs(now_n, self.children_left[now_n], False, depth + 1)
                dfs(now_n, self.children_right[now_n], True, depth + 1)

        dfs(-1, 0, True, 1)

        return self.DM_TABLES

    def get_rule_count(self):
        return self.dm_count


if __name__ == "__main__":
    clf = None
    with open('DM_rf.pickle', 'rb') as f:
        clf = pickle.load(f)

    es = clf.estimators_[0]

    features = ['dur', 'sbytes', 'dbytes',
                'sttl', 'dttl', 'spkts', 'dpkts']

    tna = DirectMapping(es, features)
