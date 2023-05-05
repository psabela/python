### Setup Environment

1. Install Anaconda3 (docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)

`pip install conda`

2. Create and activate virtual environment

    List existing virtual environments (`conda env list` or `conda info -e`)

`conda create -n snowenv python=3.8 anaconda`

`conda activate ./snowenv`

3. Install Snowpark packages

`pip install snowflake-snowpark-python`

`pip install "snowflake-snowpakr-python[pandas]"`

4. Optional snowflake connectors

`pip install snowflake-ingest`

`pip install snowflake-sqlalchemy`

5. Install Jupyter Notebooks

`pip install jupyter`

6. Create jupyter notebook project.  Navitage to folder where you want the project.

`jupyter notebook'

### Example 1: Create UDF, publish and exectue it in Snowflake.

```

#snowpark
from snowflake.snowpark.session import Session 
from snowflake.snowpark.functions import * 
from snowflake.snowpark.types import * 
from snowflake.snwopark.version import VERSION 

#pandas and json 
import pandas as pd 
import numpy as np 
import json 

#auth 
from cred_file import creds 

    #cred_file: 
    #**********
    #creds={ 
    # "account":'<account_info>', 
    # "user":"<username>", 
    # "password":'*******', 
    # "role":'<role_name>', 
    # "database":'<database_name>', 
    # "schema":'<schema_name>',
    # "warehouse":'<warehouse_name>' 
    #}

session = Session.builder.configs(creds).create()

#example of putting local file to snowflake internal stage 
session.file.put("file_name1.csv", "@STAGE_NAME", auto_compress=False)

#create udf in snowpark and save it to snowflake 

session.add_import("@STAGE_NAME/file_name1.csv")

@sproc(name="procedure_name", replace=True, packages=["snowflake-snowpark-python","pandas"])
def procedure_name(session:snowflake.snowpark.Session) -> str: 
  
  #get content from internal storage file 
  IMPORT_DIRECTORY_NAME = "snowflake_import_directory" 
  import_dir = sys._xoptions[IMPORT_DIRECTORY_NAME]
  file_data = pd.read_csv(import_dir + "file_name1.csv", index_col = False)
  
  #get snowflake table 
  df1 = session.table('SNOWFLAKE_TABLE_NAME')
  
  #convert to pandas dataframe 
  dfp = df1.to_pandas() 
  
  #
  #dfp dataframe transformation code here
  #
  
  #write result to snowflake 
  session.write_pandas(dfp,"SNOWFLAKE_NEW_TABLENAME", auto_create_table=True)
  
  return "table was written"
  
  
#execute UDF in snowflake
session.call("procedure_name")

#access resultant table 
new_table = session.table('SNOWFLAKE_NEW_TABLENAME') 
new_table_df = new_table.to_pandas()

session.close()

```

### Example 2: Transform dataset using Snowflake lazy execution

```
#snowpark
from snowflake.snowpark.session import Session 
from snowflake.snowpark.functions import * 
from snowflake.snowpark.types import * 
from snowflake.snwopark.version import VERSION 

#pandas and json 
import pandas as pd 
import numpy as np 
import json 

#auth 
from cred_file import creds 

    #cred_file: 
    #**********
    #creds={ 
    # "account":'<account_info>', 
    # "user":"<username>", 
    # "password":'*******', 
    # "role":'<role_name>', 
    # "database":'<database_name>', 
    # "schema":'<schema_name>',
    # "warehouse":'<warehouse_name>' 
    #}

afile1 = pd.read_csv("file1.csv")

session = Session.builder.config(creds).create() 

#verify session 
snowpark_version = VERSION
print('Database              :{}'.format(session.get_current_database()))
print('Schema                :{}'.format(session.get_current_schema()))
print('Warehouse             :{}'.format(session.get_current_warehouse()))
print('Role                  :{}'.format(session.get_current_role()))
print('Snowpark for Python Version :{}.{}.{}'.format(snowpark_version[0],snowpark_version[1], snowpark_version[2]))

#create dataframe representation of table
df_tbl_lzy = session.table('TABLE1')

#remove records from table
df_tbl_lzy = df_tbl_lzy.filter((col("COL4") != ""))

#split row with a column containing comma separated values into multiple rows
split_to_table = table_function("split_to_table")
df_tbl_lzy = df_tbl_lzy \
      .join_table_function(split_to_table(df_tbl_lzy["COLUMN_WITH_COMMA_SEPARATED_VALUES"], lit(",")) \
      .over(partition_by="COL3", order_by="COL3"))
      
#select subset of columns
df_tbl_lzy = df_tbl_lzy \
      .select(col('COL3'), 
              col('COL1'),
              col('VALUE').alias('CODE_VAL'),
              when(col("COL7")=="Z", lit(1)).otherwise(lit(0)).as_("abc"))
              
#show current dataframe status
df_tbl_lzy.show(2)

#combine external and snowflake data
afile1_lzy = session.create_dataframe(afile1)

#join
df_tbl_lzy = df_tbl_lzy \
      .join(afile1_lzy, (df_tbl_lzy["COL1"] == afile1_lzy["COL1"]))
      
#select subset of columns from join
df_tbl_lzy = df_tbl_lzy \
       .select(col('COL3'), 
               col('COL1'),
               col('CODE_VAL').as_('CODE'))
              
#column names
df_tbl_lzy.schema.names

#aggregate dataset
df_tbl_lzy = df_tbl_lzy.select(col('COL1'), col('COL3')) \ 
                .group_by(col('COL1'), col('COL3')) \ 
                .agg(count('COL1').alias('TOTAL'))
                
#reshape dataset
df_tbl_lzy = df_tbl_lzy.pivot("COL3",['1','0']) \ 
                .sum(col('TOTAL')) \
                .select(col("COL1"),
                    coalesce(col("'1'"), lit(1)).name("A"),
                    coalesce(col("'0'"), lit(0)).name("B"),
                    (col("A") / (col("A") + col("B"))).name("%of total"))


#df_tbl_lzy.write_table(df_tbl_lzy, "NEW_TABLENAME", auto_create_table=True)
df_tbl_lzy.write.saveAsTable("NEW_TABLENAME")

session.close()

```





