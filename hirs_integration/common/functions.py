def configuration_fixtures(group:str,config:dict,Setting) -> None:
    def add_fixture(catagory,i,value:dict):
        PATH = group + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

        obj,new = Setting.o2.get_or_create(setting=PATH % (catagory,i))

        if new:
            obj.value = value["default_value"]
            value.setdefault("hidden",False)
            obj.hidden = value["hidden"]
            obj.field_properties = Setting.__BASE_PROPERTIES__

        for k,v in value["field_properties"]:
            obj.field_properties[k] = v
        obj.save()

        return new

    for catagory,item in config[group].items():
        add_fixture(catagory,*item,item[str(*item)])