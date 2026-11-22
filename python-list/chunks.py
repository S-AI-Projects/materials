# ==============================================================================
# Input/Output Contract for split_list:
# Preconditions:
#   - list_object: Sequence or list to divide into consecutive chunks.
#   - chunk_size: Positive integer (>= 1) determining the maximum chunk length.
# Returns:
#   - List of sliced chunks (sublists), preserving original element order.
# Observable Mutation / Purity:
#   - Pure function: does not mutate list_object; returns newly created list chunks.
# Source Precondition Fixture Anchors:
#   - chunks = [] (Anchor line establishing return accumulator)
# Domain Boundaries:
#   - Smallest valid input: list_object = [], chunk_size = 1 -> []
#   - Smallest non-empty input: list_object = [1], chunk_size = 1 -> [[1]]
#   - Ordinary input: list_object = [1, 2, 3, 4, 5], chunk_size = 2 -> [[1, 2], [3, 4], [5]]
#   - Upper boundary (chunk_size >= len): list_object = [1, 2, 3], chunk_size = 5 -> [[1, 2, 3]]
#   - Repeated-value domain boundary: list_object = [7, 7, 7, 7], chunk_size = 2 -> [[7, 7], [7, 7]]
# ==============================================================================
def split_list(list_object, chunk_size):
    """Split list_object into chunks of up to chunk_size items."""
    chunks = []
    for start in range(0, len(list_object), chunk_size):
        stop = start + chunk_size
        chunks.append(list_object[start:stop])
    return chunks
