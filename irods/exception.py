# if you're copying these from the docs, you might find the following regex helpful:
# :%s/\(\w\+\)\s\+\(-\d\+\)/\2: '\1',/g

class iRODSException(Exception):
    def __init__(self, error_id):
        Exception.__init__(self, "iRODS error %d" % error_id)

def error_code_to_exception(code):
    if code > -300000:
        cls = SystemException
    elif code > -500000:
        cls = UserInputException
    elif code > -800000:
        cls = FileDriverException
    elif code > 880000:
        cls = CatalogLibraryException
    else:
        return iRODSException(code)

    if code in cls.errors:
        execption_cls = type(cls.errors[errors], (cls,), {})
    return exception_cls()

class iRODSNamedException(iRODSException):
    pass

class SystemException(iRODSNamedException):
    errors = {
        -1000: 'SYS_SOCK_OPEN_ERR',
        -2000: 'SYS_SOCK_BIND_ERR',
        -3000: 'SYS_SOCK_ACCEPT_ERR',
        -4000: 'SYS_HEADER_READ_LEN_ERR',
        -5000: 'SYS_HEADER_WRITE_LEN_ERR',
        -6000: 'SYS_HEADER_TPYE_LEN_ERR',
        -7000: 'SYS_CAUGHT_SIGNAL',
        -8000: 'SYS_GETSTARTUP_PACK_ERR',
        -9000: 'SYS_EXCEED_CONNECT_CNT',
        -10000: 'SYS_USER_NOT_ALLOWED_TO_CONN',
        -11000: 'SYS_READ_MSG_BODY_INPUT_ERR',
        -12000: 'SYS_UNMATCHED_API_NUM',
        -13000: 'SYS_NO_API_PRIV',
        -14000: 'SYS_API_INPUT_ERR',
        -15000: 'SYS_PACK_INSTRUCT_FORMAT_ERR',
        -16000: 'SYS_MALLOC_ERR',
        -17000: 'SYS_GET_HOSTNAME_ERR',
        -18000: 'SYS_OUT_OF_FILE_DESC',
        -19000: 'SYS_FILE_DESC_OUT_OF_RANGE',
        -20000: 'SYS_UNRECOGNIZED_REMOTE_FLAG',
        -21000: 'SYS_INVALID_SERVER_HOST',
        -22000: 'SYS_SVR_TO_SVR_CONNECT_FAILED',
        -23000: 'SYS_BAD_FILE_DESCRIPTOR',
        -24000: 'SYS_INTERNAL_NULL_INPUT_ERR',
        -25000: 'SYS_CONFIG_FILE_ERR',
        -26000: 'SYS_INVALID_ZONE_NAME',
        -27000: 'SYS_COPY_LEN_ERR',
        -28000: 'SYS_PORT_COOKIE_ERR',
        -29000: 'SYS_KEY_VAL_TABLE_ERR',
        -30000: 'SYS_INVALID_RESC_TYPE',
        -31000: 'SYS_INVALID_FILE_PATH',
        -32000: 'SYS_INVALID_RESC_INPUT',
        -33000: 'SYS_INVALID_PORTAL_OPR',
        -34000: 'SYS_PARA_OPR_NO_SUPPORT',
        -35000: 'SYS_INVALID_OPR_TYPE',
        -36000: 'SYS_NO_PATH_PERMISSION',
        -37000: 'SYS_NO_ICAT_SERVER_ERR',
        -38000: 'SYS_AGENT_INIT_ERR',
        -39000: 'SYS_PROXYUSER_NO_PRIV',
        -40000: 'SYS_NO_DATA_OBJ_PERMISSION',
        -41000: 'SYS_DELETE_DISALLOWED',
        -42000: 'SYS_OPEN_REI_FILE_ERR',
        -43000: 'SYS_NO_RCAT_SERVER_ERR',
        -44000: 'SYS_UNMATCH_PACK_INSTRUCTI_NAME',
        -45000: 'SYS_SVR_TO_CLI_MSI_NO_EXIST',
        -46000: 'SYS_COPY_ALREADY_IN_RESC',
        -47000: 'SYS_RECONN_OPR_MISMATCH',
        -48000: 'SYS_INPUT_PERM_OUT_OF_RANGE',
        -49000: 'SYS_FORK_ERROR',
        -50000: 'SYS_PIPE_ERROR',
        -51000: 'SYS_EXEC_CMD_STATUS_SZ_ERROR',
        -52000: 'SYS_PATH_IS_NOT_A_FILE',
        -53000: 'SYS_UNMATCHED_SPEC_COLL_TYPE',
        -54000: 'SYS_TOO_MANY_QUERY_RESULT',
        -55000: 'SYS_SPEC_COLL_NOT_IN_CACHE',
        -56000: 'SYS_SPEC_COLL_OBJ_NOT_EXIST',
        -57000: 'SYS_REG_OBJ_IN_SPEC_COLL',
        -58000: 'SYS_DEST_SPEC_COLL_SUB_EXIST',
        -59000: 'SYS_SRC_DEST_SPEC_COLL_CONFLICT',
        -60000: 'SYS_UNKNOWN_SPEC_COLL_CLASS',
        -61000: 'SYS_DUPLICATE_XMSG_TICKET',
        -62000: 'SYS_UNMATCHED_XMSG_TICKET',
        -63000: 'SYS_NO_XMSG_FOR_MSG_NUMBER',
        -64000: 'SYS_COLLINFO_2_FORMAT_ERR',
        -65000: 'SYS_CACHE_STRUCT_FILE_RESC_ERR',
        -66000: 'SYS_NOT_SUPPORTED',
        -67000: 'SYS_TAR_STRUCT_FILE_EXTRACT_ERR',
        -68000: 'SYS_STRUCT_FILE_DESC_ERR',
        -69000: 'SYS_TAR_OPEN_ERR',
        -70000: 'SYS_TAR_EXTRACT_ALL_ERR',
        -71000: 'SYS_TAR_CLOSE_ERR',
        -72000: 'SYS_STRUCT_FILE_PATH_ERR',
        -73000: 'SYS_MOUNT_MOUNTED_COLL_ERR',
        -74000: 'SYS_COLL_NOT_MOUNTED_ERR',
        -75000: 'SYS_STRUCT_FILE_BUSY_ERR',
        -76000: 'SYS_STRUCT_FILE_INMOUNTED_COLL',
        -77000: 'SYS_COPY_NOT_EXIST_IN_RESC',
        -78000: 'SYS_RESC_DOES_NOT_EXIST',
        -79000: 'SYS_COLLECTION_NOT_EMPTY',
        -80000: 'SYS_OBJ_TYPE_NOT_STRUCT_FILE',
        -81000: 'SYS_WRONG_RESC_POLICY_FOR_BUN_OPR',
        -82000: 'SYS_DIR_IN_VAULT_NOT_EMPTY',
        -83000: 'SYS_OPR_FLAG_NOT_SUPPORT',
        -84000: 'SYS_TAR_APPEND_ERR',
        -85000: 'SYS_INVALID_PROTOCOL_TYPE',
        -86000: 'SYS_UDP_CONNECT_ERR',
        -89000: 'SYS_UDP_TRANSFER_ERR',
        -90000: 'SYS_UDP_NO_SUPPORT_ERR',
        -91000: 'SYS_READ_MSG_BODY_LEN_ERR',
        -92000: 'CROSS_ZONE_SOCK_CONNECT_ERR',
        -93000: 'SYS_NO_FREE_RE_THREAD',
        -94000: 'SYS_BAD_RE_THREAD_INX',
        -95000: 'SYS_CANT_DIRECTLY_ACC_COMPOUND_RESC',
        -96000: 'SYS_SRC_DEST_RESC_COMPOUND_TYPE',
        -97000: 'SYS_CACHE_RESC_NOT_ON_SAME_HOST',
        -98000: 'SYS_NO_CACHE_RESC_IN_GRP',
        -99000: 'SYS_UNMATCHED_RESC_IN_RESC_GRP',
        -100000: 'SYS_CANT_MV_BUNDLE_DATA_TO_TRASH',
        -101000: 'SYS_CANT_MV_BUNDLE_DATA_BY_COPY',
        -102000: 'SYS_EXEC_TAR_ERR',
        -103000: 'SYS_CANT_CHKSUM_COMP_RESC_DATA',
        -104000: 'SYS_CANT_CHKSUM_BUNDLED_DATA',
        -105000: 'SYS_RESC_IS_DOWN',
        -106000: 'SYS_UPDATE_REPL_INFO_ERR',
        -107000: 'SYS_COLL_LINK_PATH_ERR',
        -108000: 'SYS_LINK_CNT_EXCEEDED_ERR',
        -109000: 'SYS_CROSS_ZONE_MV_NOT_SUPPORTED',
        -110000: 'SYS_RESC_QUOTA_EXCEEDED',
    }

class UserInputException(iRODSNamedException):
    error = {
        -300000: 'USER_AUTH_SCHEME_ERR',
        -301000: 'USER_AUTH_STRING_EMPTY',
        -302000: 'USER_RODS_HOST_EMPTY',
        -303000: 'USER_RODS_HOSTNAME_ERR',
        -304000: 'USER_SOCK_OPEN_ERR',
        -305000: 'USER_SOCK_CONNECT_ERR',
        -306000: 'USER_STRLEN_TOOLONG',
        -307000: 'USER_API_INPUT_ERR',
        -308000: 'USER_PACKSTRUCT_INPUT_ERR',
        -309000: 'USER_NO_SUPPORT_ERR',
        -310000: 'USER_FILE_DOES_NOT_EXIST',
        -311000: 'USER_FILE_TOO_LARGE',
        -312000: 'OVERWITE_WITHOUT_FORCE_FLAG',
        -313000: 'UNMATCHED_KEY_OR_INDEX',
        -314000: 'USER_CHKSUM_MISMATCH',
        -315000: 'USER_BAD_KEYWORD_ERR',
        -316000: 'USER__NULL_INPUT_ERR',
        -317000: 'USER_INPUT_PATH_ERR',
        -318000: 'USER_INPUT_OPTION_ERR',
        -319000: 'USER_INVALID_USERNAME_FORMAT',
        -320000: 'USER_DIRECT_RESC_INPUT_ERR',
        -321000: 'USER_NO_RESC_INPUT_ERR',
        -322000: 'USER_PARAM_LABEL_ERR',
        -323000: 'USER_PARAM_TYPE_ERR',
        -324000: 'BASE64_BUFFER_OVERFLOW',
        -325000: 'BASE64_INVALID_PACKET',
        -326000: 'USER_MSG_TYPE_NO_SUPPORT',
        -337000: 'USER_RSYNC_NO_MODE_INPUT_ERR',
        -338000: 'USER_OPTION_INPUT_ERR',
        -339000: 'SAME_SRC_DEST_PATHS_ERR',
        -340000: 'USER_RESTART_FILE_INPUT_ERR',
        -341000: 'RESTART_OPR_FAILED',
        -342000: 'BAD_EXEC_CMD_PATH',
        -343000: 'EXEC_CMD_OUTPUT_TOO_LARGE',
        -344000: 'EXEC_CMD_ERROR',
        -345000: 'BAD_INPUT_DESC_INDEX',
        -346000: 'USER_PATH_EXCEEDS_MAX',
        -347000: 'USER_SOCK_CONNECT_TIMEDOUT',
        -348000: 'USER_API_VERSION_MISMATCH',
        -349000: 'USER_INPUT_FORMAT_ERR',
        -350000: 'USER_ACCESS_DENIED',
        -351000: 'CANT_RM_MV_BUNDLE_TYPE',
        -352000: 'NO_MORE_RESULT',
        -353000: 'NO_KEY_WD_IN_MS_INP_STR',
        -354000: 'CANT_RM_NON_EMPTY_HOME_COLL',
        -355000: 'CANT_UNREG_IN_VAULT_FILE',
        -356000: 'NO_LOCAL_FILE_RSYNC_IN_MSI',
    }

class FileDriverException(iRODSNamedException):
    errors = {
        -500000: 'FILE_INDEX_LOOKUP_ERR', 
        -510000: 'UNIX_FILE_OPEN_ERR', 
        -511000: 'UNIX_FILE_CREATE_ERR', 
        -512000: 'UNIX_FILE_READ_ERR', 
        -513000: 'UNIX_FILE_WRITE_ERR', 
        -514000: 'UNIX_FILE_CLOSE_ERR', 
        -515000: 'UNIX_FILE_UNLINK_ERR', 
        -516000: 'UNIX_FILE_STAT_ERR', 
        -517000: 'UNIX_FILE_FSTAT_ERR', 
        -518000: 'UNIX_FILE_LSEEK_ERR', 
        -519000: 'UNIX_FILE_FSYNC_ERR', 
        -520000: 'UNIX_FILE_MKDIR_ERR', 
        -521000: 'UNIX_FILE_RMDIR_ERR', 
        -522000: 'UNIX_FILE_OPENDIR_ERR', 
        -523000: 'UNIX_FILE_CLOSEDIR_ERR', 
        -524000: 'UNIX_FILE_READDIR_ERR', 
        -525000: 'UNIX_FILE_STAGE_ERR', 
        -526000: 'UNIX_FILE_GET_FS_FREESPACE_ERR', 
        -527000: 'UNIX_FILE_CHMOD_ERR', 
        -528000: 'UNIX_FILE_RENAME_ERR', 
        -529000: 'UNIX_FILE_TRUNCATE_ERR', 
        -530000: 'UNIX_FILE_LINK_ERR',
    }

class CatalogLibraryError(iRODSNamedException):
    errors = {
        -801000: 'CATALOG_NOT_CONNECTED',
        -802000: 'CAT_ENV_ERR',
        -803000: 'CAT_CONNECT_ERR',
        -804000: 'CAT_DISCONNECT_ERR',
        -805000: 'CAT_CLOSE_ENV_ERR',
        -806000: 'CAT_SQL_ERR',
        -807000: 'CAT_GET_ROW_ERR',
        -808000: 'CAT_NO_ROWS_FOUND',
        -809000: 'CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME',
        -810000: 'CAT_INVALID_RESOURCE_TYPE',
        -811000: 'CAT_INVALID_RESOURCE_CLASS',
        -812000: 'CAT_INVALID_RESOURCE_NET_ADDR',
        -813000: 'CAT_INVALID_RESOURCE_VAULT_PATH',
        -814000: 'CAT_UNKNOWN_COLLECTION',
        -815000: 'CAT_INVALID_DATA_TYPE',
        -816000: 'CAT_INVALID_ARGUMENT',
        -817000: 'CAT_UNKNOWN_FILE',
        -818000: 'CAT_NO_ACCESS_PERMISSION',
        -819000: 'CAT_SUCCESS_BUT_WITH_NO_INFO',
        -820000: 'CAT_INVALID_USER_TYPE',
        -821000: 'CAT_COLLECTION_NOT_EMPTY',
        -822000: 'CAT_TOO_MANY_TABLES',
        -823000: 'CAT_UNKNOWN_TABLE',
        -824000: 'CAT_NOT_OPEN',
        -825000: 'CAT_FAILED_TO_LINK_TABLES',
        -826000: 'CAT_INVALID_AUTHENTICATION',
        -827000: 'CAT_INVALID_USER',
        -828000: 'CAT_INVALID_ZONE',
        -829000: 'CAT_INVALID_GROUP',
        -830000: 'CAT_INSUFFICIENT_PRIVILEGE_LEVEL',
        -831000: 'CAT_INVALID_RESOURCE',
        -832000: 'CAT_INVALID_CLIENT_USER',
        -833000: 'CAT_NAME_EXISTS_AS_COLLECTION',
        -834000: 'CAT_NAME_EXISTS_AS_DATAOBJ',
        -835000: 'CAT_RESOURCE_NOT_EMPTY',
        -836000: 'CAT_NOT_A_DATAOBJ_AND_NOT_A_COLLECTION',
        -837000: 'CAT_RECURSIVE_MOVE',
        -838000: 'CAT_LAST_REPLICA',
        -839000: 'CAT_OCI_ERROR',
        -840000: 'CAT_PASSWORD_EXPIRED',
        -850000: 'CAT_PASSWORD_ENCODING_ERROR',
        -851000: 'CAT_TABLE_ACCESS_DENIED',
    }
