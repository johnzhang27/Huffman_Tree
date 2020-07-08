import bitio
import huffman
import pickle


def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''

    tree_root = pickle.load(tree_stream)

    return(tree_root)


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """

    # Use isinstance as a condition of the while loop, stop while loop
    # when tree is a treeleaf in huffman tree and return the value of
    # the tree leaf.
    while not isinstance(tree,huffman.TreeLeaf):

      bit_read = bitreader.readbit()


      if bit_read == 0:
        tree = tree.getLeft()
      elif bit_read == 1:
        tree = tree.getRight()

    if isinstance(tree,huffman.TreeLeaf):
      return tree.getValue()


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''

    # Make bitreader/bitwriter and use read_tree to get the huffman tree.
    mybitreader_com = bitio.BitReader(compressed)
    mytree = read_tree(compressed)
    mybitwriter_uncom = bitio.BitWriter(uncompressed)
    end_of_file = False
    # decode the 1st byte to check if it is None(end of file) or valid.
    decoded = decode_byte(mytree,mybitreader_com)
    # We want the while loop to stop when meet EOF and when decoded = None.
    # None is kind of equal to EOF, represent there is nothing to write.
    while not end_of_file and decoded is not None:
      try:
        mybitwriter_uncom.writebits(decoded,8)
        decoded = decode_byte(mytree,mybitreader_com)

      except EOFError:
        end_of_file = True


    mybitwriter_uncom.flush()

def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree,tree_stream)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    write_tree(tree,compressed)
    # Making bitreader and bitwriter but this time is opposite to  what I
    # did in decompress. This time compressed become bitwriter and decompresed
    # become bitreader.
    mybitwriter_com = bitio.BitWriter(compressed)
    mybitreader_uncom = bitio.BitReader(uncompressed)
    table = huffman.make_encoding_table(tree)
    end_of_file = False
    # Use a while loop to write bytes(path) into compressed file. Also use
    # table to store keys and values(path) from uncompressed file.
    while not end_of_file:
      try:
        encode = mybitreader_uncom.readbits(8)

        path = table[encode]
        for i in path:
          mybitwriter_com.writebit(i)
      # We want the while loop stop when meet end of file but since
      # end of file is also a leaf in huffman tree so we need to write
      # the path to None in to compressed as well.
      except EOFError:
        end_of_file = True
        path1 = table[None]
        for i in path1:
          mybitwriter_com.writebit(i)

    mybitwriter_com.flush()
