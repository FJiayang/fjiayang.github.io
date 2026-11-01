{
  "title": "elasticsearch原生json操作笔记",
  "date": "2018-05-21T07:28:00+08:00",
  "lastmod": "2023-09-07T15:04:25+08:00",
  "typecho_cid": 155,
  "url": "/archives/155/",
  "comments": false,
  "draft": false,
  "slug": "155",
  "categories": [
    "开发"
  ],
  "tags": [
    "elasticsearch",
    "全文搜索"
  ],
  "math": true
}

## 建立结构 ##
### 建People表 ###
方法：PUT
发送地址：http://192.168.79.138:9200/people

    {
    	"setting": {
    		"number_of_shards": 3,
    		"number_of_replicas": 1
    	},
    	"mappings": {
    		"man": {
    			"properties": {
    				"name": {
    					"type": "text"
    				},
    				"country": {
    					"type": "keyword"
    				},
    				"age": {
    					"type": "integer"
    				},
    				"data":{
    					"type": "date",
    					"format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
    				}
    			}
    		}
    	}
    }
![请输入图片描述][1]

### 建book表 ###
方法：PUT
发送地址：http://192.168.79.138:9200/book

    {
    	"setting": {
    		"number_of_shards": 3,
    		"number_of_replicas": 1
    	},
    	"mappings": {
    		"novel": {
    			"properties": {
    				"word_count": {
    					"type": "integer"
    				},
    				"author": {
    					"type": "keyword"
    				},
    				"title": {
    					"type": "text"
    				},
    				"publish_date":{
    					"type": "date",
    					"format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
    				}
    			}
    		}
    	}
    }

## 插入数据 ##
### 指定ID插入数据到people.man ###
方法：PUT
发送地址http://192.168.79.138:9200/people/man/1

    {
    	"name": "F嘉阳",
    	"country": "China",
    	"age": 21,
    	"date": "1990-05-18"
    }

![请输入图片描述][2]
#### 图形化查询检验 ####
![请输入图片描述][3]

### 不指定ID插入数据到people.man ###
方法：PUT
发送地址http://192.168.79.138:9200/people/man/

    {
    	"name": "FJY",
    	"country": "China",
    	"age": 28,
    	"date": "1990-05-18"
    }

![请输入图片描述][4]

#### 图形化查询检验 ####
![请输入图片描述][5]

## 更新 ##
### 更新字段数据 ###
方法：POST
发送地址：http://192.168.79.138:9200/people/man/1/_update

    {
    	"doc": {
    		"name": "符嘉阳"
    	}
    }

![请输入图片描述][6]
#### 图形化查询检验 ####
![请输入图片描述][7]

### 使用脚本语言更新数据 ###
方法：POST
发送地址：http://192.168.79.138:9200/people/man/1/_update

    {
    	"script": {
    		"lang": "painless",
    		"inline": "ctx._source.age += 5"
    	}
    }

![请输入图片描述][8]

#### 图形化查询检验 ####
![请输入图片描述][9]

### 使用脚本语言分离参数更新数据 ###
方法：POST
发送地址：http://192.168.79.138:9200/people/man/1/_update

    {
    	"script": {
    		"lang": "painless",
    		"inline": "ctx._source.age = params.age",
    		"params": {
    			"age": 21
    		}
    	}
    }

![请输入图片描述][10]

#### 图形化查询检验 ####
![请输入图片描述][11]

## 删除 ##
### 指定ID删除一行数据 ###
方法：DELETE
发送地址：http://192.168.79.138:9200/people/man/1
![请输入图片描述][12]

#### 图形化查询检验 ####
![请输入图片描述][13]

### 删除表 ###
方法：DELETE
发送地址：http://192.168.79.138:9200/people
![请输入图片描述][14]

## 查询 ##
### 指定ID查询 ###
方法：GET
发送地址：http://192.168.79.138:9200/book/novel/H5LbbWMBzFxBPWV2GG9d
![请输入图片描述][15]

### 查询所有 ###
方法：GET
发送地址：http://192.168.79.138:9200/book/_search
    {
    	"query": {
    		"match_all": {}
    	}
    }

![请输入图片描述][16]

### 指定查询结果大小 ###

    {
    	"query": {
    		"match_all": {}
    	},
    	"from": 1,
    	"size": 1
    }

![请输入图片描述][17]

### 查询

    {
    	"query": {
    		"match": {
    			"title": "Java"
    		}
    	}
    }

### 指定查询结果排序方法

    {
    	"query": {
    		"match": {
    			"title": "Java"
    		}
    	},
    	"sort": [
    		{
    			"publish_date": {
    				"order": "desc"
    			}
    		}
    	]
    }

### 聚合

    {
    	"aggs": {
    		"group_by_word_count": {
    			"terms": {
    				"field": "word_count"
    			}
    		}
    	}
    }
### 多字段聚合

    {
    	"aggs": {
    		"group_by_word_count": {
    			"terms": {
    				"field": "word_count"
    			}
    		},
    		"group_by_author": {
    			"terms": {
    				"field": "author"
    			}
    		}
    	}
    }

### 聚合

    {
    	"aggs": {
    		"grades_by_word_count": {
    			"stats": {
    				"field": "word_count"
    			}
    		}
    	}
    }
### 模糊匹配(默认匹配法则)

    {
    	"query": {
    		"match": {
    			"title": "Java虚拟机"
    		}
    	}
    }

### 习语匹配

    {
    	"query": {
    		"match_phrase": {
    			"title": "Java虚拟机"
    		}
    	}
    }
### 多字段模糊匹配查询

    {
    	"query": {
    		"multi_match": {
    			"query": "F嘉阳",
    			"fields": ["author","title"]
    		}
    	}
    }
### 语法查询

    {
    	"query": {
    		"query_string": {
    			"query": "ElasticSearch AND 入门"
    		}
    	}
    }
    
    {
    	"query": {
    		"query_string": {
    			"query": "(ElasticSearch AND 入门) OR PS"
    		}
    	}
    }
### 语法查询指定字段

    {
    	"query": {
    		"query_string": {
    			"query": "ElasticSearch OR 瓦",
    			"fields": ["title","author"]
    		}
    	}
    }
### 结构化查询(指定字段)

    {
    	"query": {
    		"term": {
    			"word_count": 1000
    		}
    	}
    }
    
    {
    	"query": {
    		"term": {
    			"author": "F嘉阳"
    		}
    	}
    }
### 结构化查询(指定范围)
gte->大于等于 lte->小于等于 e->equal(等于)

    {
    	"query": {
    		"range": {
    			"word_count": {
    				"gte": 1000,
    				"lte": 2000
    			}
    		}
    	}
    }
### 结构化查询(指定日期范围)

    {
    	"query": {
    		"range": {
    			"publish_date": {
    				"gte": "2018-01-01",
    				"lt": "2018-12-31"
    			}
    		}
    	}
    }
### 结构化查询(指定当前时间)

    {
    	"query": {
    		"range": {
    			"publish_date": {
    				"gte": "2018-01-01",
    				"lte": "now"
    			}
    		}
    	}
    }
### 子条件查询，使用filter
使用filter过滤器后产生缓存，下次查询速度更快

    {
    	"query": {
    		"bool": {
    			"filter": {
    				"term": {
    					"word_count": 1000
    				}
    			}
    		}
    	}
    }
### 复合条件查询-固定分数查询

    {
    	"query": {
    		"constant_score": {
    			"filter": {
    				"match": {
    					"title": "Java"
    				}
    			}
    		}
    	}
    }

### 复合条件查询-指定分数查询

    {
    	"query": {
    		"constant_score": {
    			"filter": {
    				"match": {
    					"title": "Java"
    				}
    			},
    			"boost": 2
    		}
    	}
    }

### 复合条件查询-布尔查询-指定应当满足的条件(满足其一即可)

    {
    	"query": {
    		"bool": {
    			"should": [
    					{
    						"match": {
    							"author": "F嘉阳"
    						}
    					},
    					{
    						"match": {
    							"title": "Java"
    						}
    					}
    				]
    		}
    	}
    }

### 复合条件查询-布尔查询-指定必须满足的条件(两个都必须匹配)

    {
    	"query": {
    		"bool": {
    			"must": [
    					{
    						"match": {
    							"author": "F嘉阳"
    						}
    					},
    					{
    						"match": {
    							"title": "Java"
    						}
    					}
    				]
    		}
    	}
    }

### 复合条件查询-布尔查询-过滤器

    {
    	"query": {
    		"bool": {
    			"must": [
    					{
    						"match": {
    							"author": "F嘉阳"
    						}
    					},
    					{
    						"match": {
    							"title": "PS"
    						}
    					}
    				],
    				"filter": [
    						{
    							"term": {
    								"word_count": 700
    							}
    						}
    					]
    		}
    	}
    }

### 复合条件查询-must_not

    {
    	"query": {
    		"bool": {
    			"must_not": {
    				"term": {
    					"author": "F嘉阳"
    				}
    			}
    		}
    	}
    }


  [1]: /images/recovered/3f82eddbfd457d1d6356.png
  [2]: /images/recovered/6a25a31d0bb8a017f641.png
  [3]: /images/recovered/ab0adae19d1dffd36e4d.png
  [4]: /images/recovered/a895ad64cc3ca53942dd.png
  [5]: /images/recovered/090d0f657201524efec0.png
  [6]: /images/recovered/b193b6515963ae9de164.png
  [7]: /images/recovered/97d5fece80e2f72440eb.png
  [8]: /images/recovered/d4970afc8c815d7907b9.png
  [9]: /images/recovered/25ef6ff3e1381e201d76.png
  [10]: /images/recovered/67548fd137777cda5116.png
  [11]: /images/recovered/6dcbe88645f82514b575.png
  [12]: /images/recovered/96a572df42624c3d6707.png
  [13]: /images/recovered/9a48a1bca43d3e754a15.png
  [14]: /images/recovered/922c9b344764299215dc.png
  [15]: /images/recovered/5c4e1518605d61d3a521.png
  [16]: /images/recovered/541dfed5cddcd9f86728.png
  [17]: /images/recovered/338296a585c61d8847cb.png
