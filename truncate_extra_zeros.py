# Trunctate extra zeros from decimal
# Examples:
# 0.00       => 0.0 
# 123.00     => 123.0
# 123.1230   => 123.123
# 123.123000 => 123.123

def trunc_zero(val):
    if len(val)>1 and val.endswith('0'):
        _decimal = val[:-1]
        val = trunc_zero(_decimal)
    return val


if __name__=="__main__":    
    val = "57764.0000000000000
    result = val.split('.')[0] +'.'+ trunc_zero(val.split('.')[1])
    print(result)
