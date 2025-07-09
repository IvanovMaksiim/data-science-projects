import numpy as np
import heapq
from typing import Optional, Tuple, List, Any


class KDNode:
    def __init__(self, point: np.ndarray, label: Any,
                 left: Optional['KDNode'] = None, right: Optional['KDNode'] = None, axis: int = 0):
        self.point = point
        self.label = label
        self.left = left
        self.right = right
        self.axis = axis


def build_kdtree(points: np.ndarray, labels: np.ndarray, depth: int = 0) -> Optional[KDNode]:
    if len(points) <= 1:
        return KDNode(points[0], labels[0]) if len(points) == 1 else None

    k = points.shape[1]
    axis = depth % k
    median_indx = len(points) // 2
    indx = np.argpartition(points[:, axis], median_indx)

    return KDNode(
        point=points[indx[median_indx]],
        label=labels[indx[median_indx]],
        left=build_kdtree(points[indx[:median_indx]], labels[indx[:median_indx]], depth + 1),
        right=build_kdtree(points[indx[median_indx + 1:]], labels[indx[median_indx + 1:]], depth + 1),
        axis=axis
    )


def knn(tree: KDNode, target: np.ndarray, k: int) -> List[Tuple[float, Any]]:
    best = []

    def search(node: Optional[KDNode]):
        if not node:
            return
        # евклидово
        dist = np.linalg.norm(node.point - target)
        if len(best) < k:
            heapq.heappush(best, (-dist, id(node), node))
        else:
            if dist < -best[0][0]:
                heapq.heappushpop(best, (-dist, id(node), node))

        axis = node.axis
        diff = target[axis] - node.point[axis]
        first = node.left if diff < 0 else node.right
        second = node.right if diff < 0 else node.left

        search(first)
        if len(best) < k or abs(diff) < -best[0][0]:
            search(second)

    search(tree)
    return [(-d, n.label) for d, _, n in best]
