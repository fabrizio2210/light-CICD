
/users/<ID1>/name
/users/<ID1>/password
/users/<ID1>/admin

/user_project_mapping/<user_ID>/<project_ID1>
/user_project_mapping/<user_ID>/<project_ID2>

/project_setting_mapping/<project_ID>/<name_setting1> -> <setting_ID1>
/project_setting_mapping/<project_ID>/<name_setting2> -> <setting_ID2>

/main_settings/<name_setting1> -> <setting_id1>
/main_settings/<name_setting2> -> <setting_id2>


/init_project_settings/<name_setting1> -> <setting_id1>
/init_project_settings/<name_setting2> -> <setting_id2>

/projects/<ID1>/name
/projects/<ID1>/disabled
/projects/<ID2>/name

* The executions are read from filesystem by project ID *

*ID and name should be unique not changing*
/settings/<ID1>/name
/settings/<ID1>/description
/settings/<ID1>/default_value
/settings/<ID1>/value
/settings/<ID2>/name
/settings/<ID2>/descritpion
/settings/<ID2>/default_value
/settings/<ID2>/value

/project_environment_mapping/<project_id>/<name_environment1> -> <environment_id1>

/environment/<ID1>/name
/environment/<ID1>/description
/environment/<ID1>/value


## Users table
| ID | username | password | admin |

## Settings table
| ID | name | description | default_value | value |

## Initial Project Settings table
| name | setting_ID |

## Main Settings table
| name | setting_ID |

## Projects/Settings mapping table 
| Project_ID | setting_name | setting_ID |

## Projects/Users mapping table 
| User_ID | Project_ID |

## Projects table
| ID | name | disabled | 

## Projects/Environment mapping table 
| name | Project_ID | Environment_ID |

## Environments table
| ID | name | description | value |
