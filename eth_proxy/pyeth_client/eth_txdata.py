#
# In practice it turned out that importing the whole pyethereum library in order
# to access these functions made it surprisingly difficult to install client 
# applications because of pyethereum's dependencies. This is especially 
# the case on machines running OSX, and as of this writing makes it 
# impossible to install them at all under Windows.   
#

#
# From pyethereum.transactions. Sometimes all you want is the rlp serializer class
#
# If, on the other hand, you actually want to be able to sign the data then use 
# TxDataSig, which derives from this
#
import codecs
import rlp
from rlp.sedes import big_endian_int, binary, Binary
import eth_utils as utils


address = Binary.fixed_length(20, allow_empty=True)

class TxData(rlp.Serializable):
    '''
    Serializable transaction data for signing and rlp-encoding
    
    '''
    fields = [
              ('nonce', big_endian_int),
              ('gasprice', big_endian_int),
              ('startgas', big_endian_int),
              ('to', address),
              ('value', big_endian_int),
              ('data', binary),
              ('v', big_endian_int),
              ('r', big_endian_int),
              ('s', big_endian_int),
    ]

    def __init__(self, nonce=None, gasprice=None, startgas=None, to=None, 
                 value=None, data=None, v=0, r=0, s=0):
        to = utils.normalize_address(to, allow_blank=True)
        super(TxData, self).__init__(nonce, gasprice, startgas, to, value, data, v, r, s)
                
    @staticmethod
    def createFromTxData(hexData, data_type=None):
        '''
        Creates a TxData from the hex strings returned by get[foo]TxData
        data_type can also be specified as TxData
        '''
        if data_type is None:
            data_type = UnsignedTxData
        
        if hexData[0:2] == '0x':
            hexData = hexData[2:]
        rlpTxData = codecs.decode(hexData, "hex")            
        txData =  rlp.decode(rlpTxData, data_type)
        return txData                  
             
            
    def getSignedTxData(self, v, r, s):
        """
        Sign this transaction using v, r and s - ECDSA signature 
        parameters resulting from signing:
        
            rawhash = utils.sha3(rlp.encode(self, UnsignedTxData))

        Returns a string that can be sent by eth_sendRawTransaction()
        """
        self.v = v
        self.r = r
        self.s = s
        rawTx = rlp.encode(self, TxData)
        hex_tx = '0x{0}'.format(rawTx.encode('hex'))
        return hex_tx  

    def getUnsignedTxData(self):
        '''
        returned as a 0x-prefixed hex string
        '''
        rlpData = rlp.encode(self, UnsignedTxData) 
        hex_tx = '0x{0}'.format(rlpData.encode('hex'))
        return hex_tx       
 
# See rlp about this next bit. It basically says "unsignedTxData is a TxData in
# which we will ignore the r, s and v fields when serializing.
UnsignedTxData = TxData.exclude(['v', 'r', 's'])

