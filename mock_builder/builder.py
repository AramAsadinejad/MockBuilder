from schema_parser.table import Table
from faker import Faker
from schema_parser import fields
from schema_parser.base import BaseField
from schema_parser.parser import SchemaParser
from typing import Dict,List
class MockBuilder:

    def __init__(self,parser:SchemaParser):
        self.mocks = []
        self.parser:SchemaParser = parser
        # self.table = table
        self.faker = Faker()
        self.final_str = ""
        self.__fk_dict:Dict[str,List[str]] = {}
        self.__non_fk_dict : Dict[str,List[str]] = {}



    def get_base_insert_sql(self,table:Table):
        base_str = ""
        base_str = f"INSERT INTO {table.name}"
        return base_str
    

    def get_non_fk_values(self,table:Table):
        values = []
        
        for field_name,field_obj in table.fields.items():
            if not field_obj.refrence:
                if field_obj.is_primary_key:
                    pass
                elif isinstance(field_obj,fields.IntegerField):
                    values.append(str(self.faker.random_int()))
                elif isinstance(field_obj,fields.StringField):
                    values.append(f"'{self.faker.word()}'")
        return values
    

    def get_fk_fields(self,table:Table):
        fields = []
        for field_name,field_obj in table.fields.items():
            if field_obj.refrence:
                fields.append(field_name)

        return fields
    

    

    def get_non_fk_fields(self,table:Table):
        non_fk_fields = []
        for field_name,field_obj in table.fields.items():
            if not field_obj.refrence and not field_obj.is_primary_key:
                non_fk_fields.append(field_name)
        return non_fk_fields
    

    def get_fk_fields(self,table:Table):
        fk_fields = []
        for field_name,field_obj in table.fields.items():
            if field_obj.refrence:
                fk_fields.append(field_name)
        return fk_fields
    

    def get_fk_values(self,table:Table):
        values = []
        for field_name,field_obj in table.fields.items():
            if field_obj.refrence:
                refrence_table = self.parser.get_table(field_obj.refrence)
                values.append(str(self.faker.random_int(min=1,max=refrence_table.mock_count)))
        return values
    

    def get_base_update_sql(self,table:Table):
        base_str = ""
        base_str = f"UPDATE {table.name}"
        return base_str

    def build_fk_fields(self,table:Table,pk:int):
        fk_fields = self.get_fk_fields(table)
        if len(fk_fields) ==0:
            return ""
        fk_values = self.get_fk_values(table=table)
        fk_zip = zip(fk_fields,fk_values)
        fk_list = [f"{field} = {value}" for field,value in fk_zip]
        return f"{self.get_base_update_sql(table=table)} SET {','.join(fk_list)} WHERE {table.get_primary_key()} = {pk};"
        # return values

    def build_non_fk_fields(self,table:Table):
        fk_fields = self.get_non_fk_fields(table)
        if len(fk_fields) ==0:
            return ""
        fk_values = self.get_non_fk_values(table=table)
        return f"{self.get_base_insert_sql(table=table)} ({','.join(fk_fields)}) VALUES ({','.join(fk_values)});"
        # return values

    def build_non_fk_mock(self):
        final_data:Dict[str,List[str]] = {}
        for _,table_obj in self.parser.tables.items():
            if table_obj.mock_count > 0:
                for _ in range(table_obj.mock_count):
                    value = final_data.get(table_obj.name)
                    if value:
                        value.append(self.build_non_fk_fields(table_obj))
                    else:
                        final_data[table_obj.name] = [self.build_non_fk_fields(table_obj)]
        self.__non_fk_dict = final_data
        return self
    

    def update_for_fk_mock(self) -> Dict[str,list[list[str]]]:
        final_data:Dict[str,List[str]] = {}
        for _,table_obj in self.parser.tables.items():
            if table_obj.has_foreign_key():
                if table_obj.mock_count > 0:
                    for pk in range(1,table_obj.mock_count+1):
                        value = final_data.get(table_obj.name)
                        if value:
                            value.append(self.build_fk_fields(table_obj,pk))
                        else:
                            final_data[table_obj.name] = [self.build_fk_fields(table_obj,pk)]
        self.__fk_dict = final_data
        return final_data
    

    def build_sql_commands(self):
        self.build_non_fk_mock()
        self.update_for_fk_mock()
        final =""
        for key,value in self.__non_fk_dict.items():
            for sql_str in value:
                final+=sql_str
        for key,value in self.__fk_dict.items():
            for sql_str in value:
                final+=sql_str
        return final

    


        

        
    