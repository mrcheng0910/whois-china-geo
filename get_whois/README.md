Malicious URL whois
----------------------
Malicious_URL_whois 是基于WHOIS信息特定域名监测的子系统,负责whois信息的获取与更新

## 系统安装与部署:

* 依赖环境:    
    * MySQL > 5.6.x   
    * python > 2.7.x
    * MySQL python扩展   
    *推荐使用　```sudo apt-get install mysql-python``` 安装*
    * python 第三方库,详细依赖环境请见 ```requirements.txt```    
    *推荐使用 ```sudo pip install -r requirement.txt```*
* 系统安装:
    * 程序入口 : **main.py**
    * 子系统由网站后台服务器自动调用，无需手动开启
    * 修改程序配置文件中的对应选项以适配即可
        * 数据库配置项中请提供一个**拥有读写权限**的账户及**对应系统数据库的各表名称**
* 目录结构:   
    * **MaliciousURlWhois**  
    ├──**Database**　　　　　　　　　　　　　　　// 数据库模块  
    │   ├── \_\_init\_\_.py             // 模块描述文件    
    │   ├── db_opreation.py             // 数据库操作封装  
    │   ├── update_record.py            // whois记录更新
    ├──**Setting**                          // 配置模块     
    │   ├──\_\_init\_\_.py                  // 模块描述文件     
    │   ├──global_resource.py           // 系统公共资源     
    │   ├──logger.conf                  // 日志配置文件      
    │   ├──setting.json                 // 系统配置文件     
    │   ├──static.py                    // 系统静态资源        
    ├──**WhoisConnect**                     // whois通信模块     
    │   ├── \_\_init\_\_.py             // 模块描述文件     
    │   ├── proxy_socks.py              // 代理socks         
    │   ├── server_ip.py                // 获取whois服务器ip        
    │   ├── socks.py                    // Sockset        
    │   ├── whois_connect.py            // 连接whois服务器        
    │   ├── whois_tld.py                // 获取whois服务器地址        
    ├──**WhoisData**                        // whois数据处理模块        
    │   ├──.tld_set                     // tldextract缓存文件     
    │   ├──\_\_init\_\_.py                  // 模块描述文件      
    │   ├──domain_analyse.py            // 域名分析        
    │   ├──domain_status.py             // 域名状态值     
    │   ├──get_whois_func.py            // 获取whois信息处理函数        
    │   ├──info_deal.py                 // 处理whois信息     
    │   ├──service_function.dat         // whois信息处理函数配置     
    │   ├──tldextract.py                // 域名分析            
    │   ├──whois_func.py                // whois信息处理函数           
    ├──get_domain_whois.py              // 获取域名whois信息          
    ├──main.py                          // 主程序入口  
    ├──README.md                        // 描述文档    
    ├──requirements.txt                 // 依赖环境     
    └──running.log                      // 运行日志   
    
## 数据说明:

*   数据库表说明  *(详细说明见malicious_url_whois.SQL 中的注释)*
    *   fqdn    // 全域名表
    *   domain  // 域名表
    *   whois   // whois数据表
    *   whowas  // whowas数据表
    *   whois_proxy     //  代理socks表
    *   whois_srvip     //  whois 服务器ip表
    *   whois_tld_addr  //  tld,whois服务器映射关系表
    *   whowas_cookie   //  whowas缓存表
    *   domain_sum_by_day   // 后台服务器统计表
*   部分数据项说明
    *   whois_flag  (存在于domain,whois表中)         
    
		whois_flag  | 含义         
		:-------------: | :-------:|                    
		0                | 尚未处理/_无法处理_ *(无法获取whois服务器地址或其他原因)*
		1                | 正常
		-1               | 超时
		-2               | DNS异常
		-3               | sockset意外关闭
		-4               | 其他位置原因
		-5               | 获取的是**空数据**/查询速度过快		
					 
    *   whowas_flag (存在于domain,whowas表中) 
        *   详见whowas子系统说明   
  
## 其他功能说明:

   *  开启代理socoket
    * 1,将 **../Setting/setting.json** 中的 **proxySocks** 设置为 **true**    
		```"proxySocks":true```
	* 2,将代理sockset信息*[ip],[端口],[类型],[用户;密码]* 插入 whois_proxy 表中
	* 3,重启系统

   * 覆盖新的顶级域
	* 1,获取新顶级域的**whois服务器地址,ip地址(可选)**
	* 2,将***whois地址与tld***对应插入 **whois_tld_addr** 表中
	* 3,将***whois地址与ip***插入 **whois_srvip** 表中 (可选)
	* 4,将此顶级域对应的提取函数名称与whois服务器写入**service_function.dat**,将提取函数放入**whois_func.py**中
	* 5,重启系统
	  * *关于提取函数写法可参照**whois_func.py**中其他提取函数和whois服务器返回数据格式*
	
   * 数据库结构变更
     * 请不要变更子系统依赖数据表(**whois_proxy,whois_tld_addr,whois_srvip**)的结构 
     * 将**whois**表结构修改后,程序**全部**的**SQL语句**均集中在**../DataBase/update_record.py**中,按找当前结构修改写入SQL语句即可
	
   * 运行日志说明  
	* 查看运行日志 **running.log** 将会帮助您更方便的理解程序及处理异常
	* 系统自动保留 **最近三天** 的日志
    * 您可能会在日志中见到集中常见错误:
	    * whois通信地址获取失败 :*表示当前域名的whois服务器地址不在数据库中*   
	    * MySQL语句错误 : 由与**未预计的返回数据编码** 或者 **极其特别的whois数据** 导致的数据库读写异常
	      * *为了获取 **中文** whois数据,数据库采用了**utf-8编码**,在处理**日文,韩文,其他非英文语言时**数据时可能会报错,在日志中也会记录此类域名的**原始whois信息***
	    * 其他异常及错误

## 最后:
  * 联系方式 : **z.g.13@163.com**/**h.j.13.new@gmail.com** 
  * 哈尔滨工业大学(威海)
  * 2017年02月13日 
   
  