import csv
import random
import math

def read_data(csv_path):
    """Read in the training data from a csv file.
    
    The examples are returned as a list of Python dictionaries, with column names as keys.
    """
    examples = []
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for example in csv_reader:
            for k, v in example.items():
                if v == '':
                    example[k] = None
                else:
                    try:
                        example[k] = float(v)
                    except ValueError:
                         example[k] = v
            examples.append(example)
    return examples


def train_test_split(examples, test_perc):
    """Randomly data set (a list of examples) into a training and test set."""
    test_size = round(test_perc*len(examples))    
    shuffled = random.sample(examples, len(examples))
    return shuffled[test_size:], shuffled[:test_size]


class TreeNodeInterface():
    """Simple "interface" to ensure both types of tree nodes must have a classify() method."""
    def classify(self, example): 
        pass


class DecisionNode(TreeNodeInterface):
    """Class representing an internal node of a decision tree."""

    def __init__(self, test_attr_name, test_attr_threshold, child_lt, child_ge, child_miss):
        """Constructor for the decision node.  Assumes attribute values are continuous.

        Args:
            test_attr_name: column name of the attribute being used to split data
            test_attr_threshold: value used for splitting
            child_lt: DecisionNode or LeafNode representing examples with test_attr_name
                values that are less than test_attr_threshold
            child_ge: DecisionNode or LeafNode representing examples with test_attr_name
                values that are greater than or equal to test_attr_threshold
            child_miss: DecisionNode or LeafNode representing examples that are missing a
                value for test_attr_name                 
        """    
        self.test_attr_name = test_attr_name  
        self.test_attr_threshold = test_attr_threshold 
        self.child_ge = child_ge
        self.child_lt = child_lt
        self.child_miss = child_miss

    def classify(self, example):
        """Classify an example based on its test attribute value.
        
        Args:
            example: a dictionary { attr name -> value } representing a data instance

        Returns: a class label and probability as tuple
        """
        test_val = example[self.test_attr_name]
        if test_val is None:
            return self.child_miss.classify(example)
        elif test_val < self.test_attr_threshold:
            return self.child_lt.classify(example)
        else:
            return self.child_ge.classify(example)

    def __str__(self):
        return "test: {} < {:.4f}".format(self.test_attr_name, self.test_attr_threshold) 


class LeafNode(TreeNodeInterface):
    """Class representing a leaf node of a decision tree.  Holds the predicted class."""

    def __init__(self, pred_class, pred_class_count, total_count):
        """Constructor for the leaf node.

        Args:
            pred_class: class label for the majority class that this leaf represents
            pred_class_count: number of training instances represented by this leaf node
            total_count: the total number of training instances used to build the leaf node
        """    
        self.pred_class = pred_class
        self.pred_class_count = pred_class_count
        self.total_count = total_count
        self.prob = pred_class_count / total_count  # probability of having the class label

    def classify(self, example):
        """Classify an example.
        
        Args:
            example: a dictionary { attr name -> value } representing a data instance

        Returns: a class label and probability as tuple as stored in this leaf node.  This will be
            the same for all examples!
        """
        return self.pred_class, self.prob

    def __str__(self):
        return "leaf {} {}/{}={:.2f}".format(self.pred_class, self.pred_class_count, 
                                             self.total_count, self.prob)


class DecisionTree:
    """Class representing a decision tree model."""

    def __init__(self, examples, id_name, class_name, min_leaf_count=1):
        """Constructor for the decision tree model.  Calls learn_tree().

        Args:
            examples: training data to use for tree learning, as a list of dictionaries
            id_name: the name of an identifier attribute (ignored by learn_tree() function)
            class_name: the name of the class label attribute (assumed categorical)
            min_leaf_count: the minimum number of training examples represented at a leaf node
        """
        self.id_name = id_name
        self.class_name = class_name
        self.min_leaf_count = min_leaf_count
        self.max_depth = 10
        self.cur_depth = 0

        # build the tree!
        self.root = self.learn_tree(examples)  

    def learn_tree(self, examples):
        """Build the decision tree based on entropy and information gain.
        
        Args:
            examples: training data to use for tree learning, as a list of dictionaries.  The
                attribute stored in self.id_name is ignored, and self.class_name is consided
                the class label.
        
        Returns: a DecisionNode or LeafNode representing the tree
        """
        self.cur_depth += 1
        
        best_split = self.nextsplit(examples)
        
        if best_split["infogain"]< 0.9 and self.cur_depth <= self.max_depth :
            lsub = self.nextsplit(best_split["leftChild"])
            lthresh = lsub["infogain"]#infogain of left sub tree 
            rsub = self.nextsplit(best_split["rightChild"])

            rthresh = rsub["infogain"]#infogain of right child
            print(rthresh)
            if lthresh > rthresh:
                return DecisionNode(lsub['attribute'],lsub['threshold'],self.learn_tree(lsub['leftChild']),self.learn_tree(lsub['rightChild']),lsub['missChild'])
            else:
               return DecisionNode(rsub['attribute'],rsub['threshold'],self.learn_tree(rsub['leftChild']),self.learn_tree(rsub['rightChild']),rsub['missChild'])
        else:
            lsub = self.nextsplit(best_split["leftChild"])
            lthresh = lsub["infogain"]#infogain of left sub tree 
            rsub = self.nextsplit(best_split["rightChild"])
            rthresh = rsub["infogain"]#infogain of right child
            print(rthresh)
            if len(best_split['leftChild']) < self.min_leaf_count or len(best_split['rightChild']) < self.min_leaf_count:
                return LeafNode(self.labelfinder(examples),len(examples),len(examples))
            elif lthresh > rthresh:
                return LeafNode(self.labelfinder(lsub['leftChild']),len(lsub['leftChild']),len(best_split))
            else:
                return LeafNode(self.labelfinder(rsub['rightChild']),len(rsub['rightChild'],len(best_split)))

    def labelfinder(dataset):
        labellist = self.pullData(dataset)
        labels = list(set(labellist))#unique list
        labeldict = dict()
        for label in labels:
            freq = labellist.count(label)
            labeldict[label] = freq
        return max(labeldict, key = labeldict.get)

    def classify(self, example):
        """Perform inference on a single example.

        Args:
            example: the instance being classified

        Returns: a tuple containing a class label and a probability
        """
        #
        # fill in the function body here!
        #
        #use root to iterate through the tree
        #when advancing a node down, check if we are going to a decision node or a leaf node 
        #if leaf node -> check predicted class as that is our assumed answer
        #if decision node, see if conditon is met -> if yes we get a leaf node, if not then we move to the next decision node 


        return "hello", 0.42  # fix this line!

    def nextsplit(self, dataset):
        split = dict()
        IG = -float("inf")
        leftChild = []
        rightChild = []

        attr_list = dataset[0].keys()
        vals = []
        miss_child = []
        for key in attr_list:
            if key != 'town' and key != '2020_label':
                for i in range(0,len(dataset)):
                    if dataset[i][key]:
                        vals.append(dataset[i][key])
                    else:
                        miss_child.append(dataset[i])
                vals = list(set(vals))#unique list of values for a particular attribute
                for threshold in vals:
                    leftChild, rightChild = self.splitter(dataset, key, threshold)
                    if len(leftChild) > 0 and len(rightChild) > 0:
                        tot = self.pullData(dataset)
                        left = self.pullData(leftChild)
                        right = self.pullData(rightChild)
                        ig = self.infoGain(tot, left, right)
                        if ig > IG:
                            split["attribute"] = key
                            split["leftChild"] = leftChild
                            split["rightChild"]= rightChild
                            split["infogain"] = ig
                            IG = ig
                            split["threshold"] = threshold
                            split["missChild"] = miss_child
        return split


    def pullData(self, data):
        arrayData = []
        for i in range(0,len(data)):
            arrayData.append(data[i]['2020_label'])
        return arrayData

    def splitter(self, data, key, threshold):
        larray = []
        rarray = []

        for i in range(0, len(data)):
            if data[i][key]:
                if data[i][key] > threshold:
                    rarray.append(data[i])
                else:
                    larray.append(data[i])
        return larray,rarray

    def infoGain(self, parent, left, right):
        lweight = len(left)/len(parent)
        rweight = len(right)/len(parent)
        infogain = self.entropy(parent) - (lweight*self.entropy(left)+rweight*self.entropy(right))
        return infogain

    def entropy(self, arr):
        label = list(set(arr))
        entropy = 0.0
        for item in label:
            freq = arr.count(item)
            prob = freq/len(arr)
            entropy+= (-prob)* math.log2(prob)
        return entropy

    def __str__(self):
        """String representation of tree, calls _ascii_tree()."""
        ln_bef, ln, ln_aft = self._ascii_tree(self.root)
        return "\n".join(ln_bef + [ln] + ln_aft)

    def _ascii_tree(self, node):
        """Super high-tech tree-printing ascii-art madness."""
        indent = 7  # adjust this to decrease or increase width of output 
        if type(node) == LeafNode:
            return [""], "leaf {} {}/{}={:.2f}".format(node.pred_class, node.pred_class_count, node.total_count, node.prob), [""]  
        else:
            child_ln_bef, child_ln, child_ln_aft = self._ascii_tree(node.child_ge)
            lines_before = [ " "*indent*2 + " " + " "*indent + line for line in child_ln_bef ]            
            lines_before.append(" "*indent*2 + u'\u250c' + " >={}----".format(node.test_attr_threshold) + child_ln)
            lines_before.extend([ " "*indent*2 + "|" + " "*indent + line for line in child_ln_aft ])

            line_mid = node.test_attr_name
            
            child_ln_bef, child_ln, child_ln_aft = self._ascii_tree(node.child_lt)
            lines_after = [ " "*indent*2 + "|" + " "*indent + line for line in child_ln_bef ]
            lines_after.append(" "*indent*2 + u'\u2514' + "- <{}----".format(node.test_attr_threshold) + child_ln)
            lines_after.extend([ " "*indent*2 + " " + " "*indent + line for line in child_ln_aft ])

            return lines_before, line_mid, lines_after


def confusion4x4(labels, vals):
    """Create an normalized predicted vs. actual confusion matrix for four classes."""
    n = sum([ v for v in vals.values() ])
    abbr = [ "".join(w[0] for w in lab.split()) for lab in labels ]
    s =  ""
    s += " actual ___________________________________  \n"
    for ab, labp in zip(abbr, labels):
        row = [ vals.get((labp, laba), 0)/n for laba in labels ]
        s += "       |        |        |        |        | \n"
        s += "  {:^4s} | {:5.2f}  | {:5.2f}  | {:5.2f}  | {:5.2f}  | \n".format(ab, *row)
        s += "       |________|________|________|________| \n"
    s += "          {:^4s}     {:^4s}     {:^4s}     {:^4s} \n".format(*abbr)
    s += "                     predicted \n"
    return s


#############################################

if __name__ == '__main__':

    path_to_csv = 'town_data.csv'
    class_attr_name = '2020_label'
    id_attr_name = 'town'
    min_examples = 10  # minimum number of examples for a leaf node

    # read in the data
    examples = read_data(path_to_csv)
    train_examples, test_examples = train_test_split(examples, 0.25)

    # learn a tree from the training set
    tree = DecisionTree(train_examples, id_attr_name, class_attr_name, min_examples)

    # test the tree on the test set and see how we did
    correct = 0
    almost = 0  # within one level of correct answer
    ordering = ['red', 'light blue', 'medium blue', 'wicked blue']  # used to count "almost" right
    test_act_pred = {}
    for example in test_examples:
        actual = example[class_attr_name]
        pred, prob = tree.classify(example)
        print("{:30} pred {:15} ({:.2f}), actual {:15} {}".format(example[id_attr_name] + ':', 
                                                            "'" + pred + "'", prob, 
                                                            "'" + actual + "'",
                                                            '*' if pred == actual else ''))
        if pred == actual:
            correct += 1
        if abs(ordering.index(pred) - ordering.index(actual)) < 2:
            almost += 1
        test_act_pred[(actual, pred)] = test_act_pred.get((actual, pred), 0) + 1 

    print("\naccuracy: {:.2f}".format(correct/len(test_examples)))
    print("almost:   {:.2f}\n".format(almost/len(test_examples)))
    print(confusion4x4(['red', 'light blue', 'medium blue', 'wicked blue'], test_act_pred))
    print(tree)  # visualize the tree in sweet, 8-bit text


