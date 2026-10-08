import { expandedProducts } from './catalog-expanded.js';
// Science Edition: all 64 models, properties, availability and prices are fictional.
// Source: supplied data/catalog_64.json; previous release names retained as aliases.
export const groups={
  "ups": {
    "icon": "battery",
    "label": "Резервне живлення",
    "filters": [
      "Потужність",
      "Виходи"
    ],
    "description": "Живлення для маршрутизатора й оптичного термінала.",
    "name": "Резервне живлення DC",
    "typeLabel": "Резервне живлення DC",
    "family": "VOLTYN",
    "keys": [
      "Потужність",
      "Запас енергії",
      "Виходи",
      "Роз’єм DC",
      "Полярність",
      "Маса"
    ],
    "numericFacetDefinitions": [
      [
        "powerW",
        "Потужність",
        "W"
      ],
      [
        "energyWh",
        "Запас енергії",
        "Wh"
      ],
      [
        "massG",
        "Маса",
        "g"
      ]
    ]
  },
  "optics": {
    "icon": "link",
    "label": "Оптичні з’єднання",
    "filters": [
      "Швидкість",
      "Роз’єм"
    ],
    "description": "Вибір за портом, конектором і довжиною лінії.",
    "name": "Оптичні модулі",
    "typeLabel": "Оптичні модулі",
    "family": "PROMYN",
    "keys": [
      "Швидкість",
      "Роз’єм",
      "Дальність",
      "Форм-фактор",
      "Волокно",
      "Моніторинг",
      "Довжина хвилі"
    ],
    "numericFacetDefinitions": [
      [
        "speedGbps",
        "Швидкість",
        "Gbps"
      ],
      [
        "distanceKm",
        "Дальність",
        "km"
      ]
    ]
  },
  "switches": {
    "icon": "network",
    "label": "Комутація мережі",
    "filters": [
      "LAN-порти",
      "PoE"
    ],
    "description": "Порти, живлення PoE та спосіб керування.",
    "name": "Мережеві комутатори",
    "typeLabel": "Мережеві комутатори",
    "family": "SVITRA",
    "keys": [
      "LAN-порти",
      "Швидкість",
      "PoE",
      "Керування",
      "SFP-порти",
      "Корпус",
      "SFP+-порти"
    ],
    "numericFacetDefinitions": [
      [
        "lanPorts",
        "LAN-порти",
        "count"
      ],
      [
        "speedGbps",
        "Швидкість",
        "Gbps"
      ],
      [
        "sfpPorts",
        "SFP-порти",
        "count"
      ],
      [
        "sfpPlusPorts",
        "SFP+-порти",
        "count"
      ]
    ]
  },
  "cable": {
    "icon": "cable",
    "label": "Кабельна інфраструктура",
    "filters": [
      "Матеріал",
      "Застосування"
    ],
    "description": "Матеріал провідника, середовище та одиниця продажу.",
    "name": "Кабель для мереж",
    "typeLabel": "Кабель для мереж",
    "family": "STRUNEX",
    "keys": [
      "Матеріал",
      "Застосування",
      "Категорія",
      "Пари",
      "Оболонка",
      "Довжина бухти",
      "Екранування"
    ],
    "numericFacetDefinitions": [
      [
        "pairs",
        "Пари",
        "count"
      ],
      [
        "reelM",
        "Довжина бухти",
        "m"
      ]
    ]
  },
  "wifi": {
    "icon": "network",
    "label": "Бездротова мережа",
    "filters": [
      "Стандарт Wi-Fi",
      "Середовище"
    ],
    "description": "Радіодіапазони, мережевий порт і спосіб монтажу.",
    "name": "Точки доступу Wi-Fi",
    "typeLabel": "Точки доступу Wi-Fi",
    "family": "ZORYX",
    "keys": [
      "Стандарт Wi-Fi",
      "Діапазони",
      "Ethernet",
      "Живлення PoE",
      "Монтаж",
      "Середовище",
      "Гранична споживана потужність"
    ],
    "numericFacetDefinitions": [
      [
        "ethernetGbps",
        "Ethernet",
        "Gbps"
      ],
      [
        "powerInputMaxW",
        "Гранична споживана потужність",
        "W"
      ]
    ]
  },
  "splitters": {
    "icon": "link",
    "label": "Розподіл оптичного сигналу",
    "filters": [
      "Коефіцієнт ділення",
      "Роз’єм"
    ],
    "description": "Коефіцієнт ділення, виконання і роз’єм.",
    "name": "Оптичні дільники PLC",
    "typeLabel": "Оптичні дільники PLC",
    "family": "FIBRYK",
    "keys": [
      "Коефіцієнт ділення",
      "Виконання",
      "Роз’єм",
      "Волокно",
      "Довжини хвиль",
      "Внесені втрати",
      "Монтаж"
    ],
    "numericFacetDefinitions": []
  },
  "meters": {
    "icon": "grid",
    "label": "Оптичні вимірювання",
    "filters": [
      "Діапазон",
      "Експорт"
    ],
    "description": "Діапазон, адаптери й збереження вимірів.",
    "name": "Вимірювачі оптичної потужності",
    "typeLabel": "Вимірювачі оптичної потужності",
    "family": "KVANTYK",
    "keys": [
      "Діапазон",
      "Адаптери",
      "Експорт",
      "Довжини хвиль",
      "Пам’ять вимірів",
      "Похибка",
      "Клас приладу"
    ],
    "numericFacetDefinitions": [
      [
        "memorySamples",
        "Пам’ять вимірів",
        "count"
      ]
    ]
  },
  "injectors": {
    "icon": "battery",
    "label": "Живлення через Ethernet",
    "filters": [
      "PoE",
      "Тип"
    ],
    "description": "Стандарт PoE, кількість портів і бюджет живлення.",
    "name": "Інжектори PoE",
    "typeLabel": "Інжектори PoE",
    "family": "MODULYN",
    "keys": [
      "PoE",
      "Сумарна вихідна потужність",
      "Потужність на порт",
      "Швидкість",
      "PoE-порти",
      "Тип",
      "Живлення"
    ],
    "numericFacetDefinitions": [
      [
        "budgetW",
        "Сумарна вихідна потужність",
        "W"
      ],
      [
        "portMaxW",
        "Потужність на порт",
        "W"
      ],
      [
        "speedGbps",
        "Швидкість",
        "Gbps"
      ],
      [
        "ports",
        "PoE-порти",
        "count"
      ]
    ]
  }
};
const coreProducts=[
  {
    "id": "u01",
    "group": "ups",
    "name": "VOLTYN N18",
    "code": "R18",
    "sku": "DEMO-U01",
    "price": 129000,
    "available": true,
    "props": {
      "Потужність": "18 Вт",
      "Запас енергії": "36 Вт·год",
      "Виходи": "9 / 12 В",
      "Роз’єм DC": "5,5 × 2,1 мм",
      "Полярність": "Плюс у центрі",
      "Маса": null
    },
    "desc": "Для одного мережевого пристрою. Компактне виконання.",
    "compat": "Спільна межа всіх виходів — 18 Вт. Звірте напругу, роз’єм і полярність пристрою. Час автономності не вимірювався.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 18",
      "Резерв DC 18",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N18",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 18,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 36,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": null,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 129000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Маса"
    ],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u02",
    "group": "ups",
    "name": "VOLTYN N36",
    "code": "R36",
    "sku": "DEMO-U02",
    "price": 219000,
    "available": true,
    "props": {
      "Потужність": "36 Вт",
      "Запас енергії": "60 Вт·год",
      "Виходи": "9 / 12 В",
      "Роз’єм DC": "5,5 × 2,1 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "520 г"
    },
    "desc": "Для двох пристроїв із загальним навантаженням до 36 Вт.",
    "compat": "Спільна межа — 36 Вт; один DC-вихід — до 24 Вт. Звірте роз’єм і полярність. Автономність залежить від фактичного навантаження.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 36",
      "Резерв DC 36",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N36",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 36,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 60,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 520,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 219000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u03",
    "group": "ups",
    "name": "VOLTYN N60",
    "code": "R60",
    "sku": "DEMO-U03",
    "price": 329000,
    "available": false,
    "props": {
      "Потужність": "60 Вт",
      "Запас енергії": "90 Вт·год",
      "Виходи": "12 / 24 В",
      "Роз’єм DC": "5,5 × 2,5 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "860 г"
    },
    "desc": "Для обладнання з напругою 12 або 24 В.",
    "compat": "Не підходить для входу 9 В. Спільна межа — 60 Вт. Штекер 5,5 × 2,5 мм слід звірити окремо.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 60",
      "Резерв DC 60",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N60",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 90,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 860,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 329000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn"
    ]
  },
  {
    "id": "u04",
    "group": "ups",
    "name": "VOLTYN N36 Arc",
    "code": "R36-P",
    "sku": "DEMO-U04",
    "price": 249000,
    "available": true,
    "props": {
      "Потужність": "36 Вт",
      "Запас енергії": "72 Вт·год",
      "Виходи": "9 / 12 В",
      "Роз’єм DC": "5,5 × 2,1 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "610 г"
    },
    "desc": "Виконання з більшим умовним запасом енергії.",
    "compat": "Демонстраційні параметри. Межа всіх виходів — 36 Вт; звірте напругу й полярність. Час автономності не вимірювався.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 36+",
      "Резерв 36 Plus",
      "Резерв DC 36 Plus",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N36 Arc",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 36,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 72,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 610,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 249000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u05",
    "group": "ups",
    "name": "VOLTYN N48",
    "code": "R48",
    "sku": "DEMO-U05",
    "price": 289000,
    "available": true,
    "props": {
      "Потужність": "48 Вт",
      "Запас енергії": "72 Вт·год",
      "Виходи": "12 / 24 В",
      "Роз’єм DC": "5,5 × 2,5 мм",
      "Полярність": "Плюс у центрі",
      "Маса": null
    },
    "desc": "Проміжне виконання для пристроїв на 12 або 24 В.",
    "compat": "Демонстраційні параметри. Не для входу 9 В. Межа — 48 Вт; масу не уточнено.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 48",
      "Резерв DC 48",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N48",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 48,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 72,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": null,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 289000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Маса"
    ],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u06",
    "group": "ups",
    "name": "VOLTYN N60 Arc",
    "code": "R60-P",
    "sku": "DEMO-U06",
    "price": 379000,
    "available": true,
    "props": {
      "Потужність": "60 Вт",
      "Запас енергії": "120 Вт·год",
      "Виходи": "12 / 24 В",
      "Роз’єм DC": "5,5 × 2,5 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "980 г"
    },
    "desc": "Більший умовний запас енергії у виконанні на 60 Вт.",
    "compat": "Демонстраційні параметри. Межа — 60 Вт; запас енергії не є обіцянкою тривалості роботи.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Резерв 60+",
      "Резерв 60 Plus",
      "Резерв DC 60 Plus",
      "voltyn",
      "Вольтин"
    ],
    "family": "VOLTYN",
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "VOLTYN N60 Arc",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 120,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 980,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 379000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u07",
    "sku": "DEMO-U07",
    "group": "ups",
    "code": "U07",
    "price": 189000,
    "available": true,
    "props": {
      "Потужність": "24 Вт",
      "Запас енергії": "48 Вт·год",
      "Виходи": "5 / 9 / 12 В",
      "Роз’єм DC": "5,5 × 2,1 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "480 г"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "VOLTYN N24",
    "family": "VOLTYN",
    "aliases": [
      "voltyn",
      "Вольтин"
    ],
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "VOLTYN N24",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 24,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 48,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 480,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 189000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "u08",
    "sku": "DEMO-U08",
    "group": "ups",
    "code": "U08",
    "price": 339000,
    "available": true,
    "props": {
      "Потужність": "48 Вт",
      "Запас енергії": "96 Вт·год",
      "Виходи": "12 / 24 В",
      "Роз’єм DC": "5,5 × 2,5 мм",
      "Полярність": "Плюс у центрі",
      "Маса": "850 г"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "VOLTYN N48 Arc",
    "family": "VOLTYN",
    "aliases": [
      "voltyn",
      "Вольтин"
    ],
    "typeLabel": "Резервне живлення DC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "VOLTYN N48 Arc",
      "Резервне живлення DC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "ups-origin",
    "demoDocument": {
      "id": "u08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "powerW": {
        "value": 48,
        "unit": "W",
        "derivedFrom": "Потужність"
      },
      "energyWh": {
        "value": 96,
        "unit": "Wh",
        "derivedFrom": "Запас енергії"
      },
      "massG": {
        "value": 850,
        "unit": "g",
        "derivedFrom": "Маса"
      },
      "priceCents": {
        "value": 339000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "ups",
      "voltyn",
      "in-stock"
    ]
  },
  {
    "id": "o01",
    "group": "optics",
    "name": "PROMYN S1 LC",
    "code": "L1-LC",
    "sku": "DEMO-O01",
    "price": 65000,
    "available": true,
    "props": {
      "Швидкість": "1 Гбіт/с",
      "Роз’єм": "LC duplex",
      "Дальність": "10 км",
      "Форм-фактор": "SFP",
      "Волокно": "Одномодове",
      "Моніторинг": "DDM"
    },
    "desc": "Двоволоконне з’єднання з роз’ємом LC.",
    "compat": "Потрібен сумісний SFP-порт 1 Гбіт/с і пара одномодових волокон. Роз’єм LC не взаємозамінний зі SC.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Лінк 1G · LC",
      "Лінк 1 LC",
      "Лінк 1G LC",
      "promyn",
      "Промін"
    ],
    "family": "PROMYN",
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "PROMYN S1 LC",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 10,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 65000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o02",
    "group": "optics",
    "name": "PROMYN S1 SC",
    "code": "L1-SC",
    "sku": "DEMO-O02",
    "price": 72000,
    "available": true,
    "props": {
      "Швидкість": "1 Гбіт/с",
      "Роз’єм": "SC duplex",
      "Дальність": "10 км",
      "Форм-фактор": "SFP",
      "Волокно": "Одномодове",
      "Моніторинг": null
    },
    "desc": "Альтернативне виконання з роз’ємом SC.",
    "compat": "Потрібен сумісний SFP-порт і двоволоконна лінія SC. Підтримку DDM не уточнено.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Лінк 1G · SC",
      "Лінк 1 SC",
      "Лінк 1G SC",
      "promyn",
      "Промін"
    ],
    "family": "PROMYN",
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "PROMYN S1 SC",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 10,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 72000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Моніторинг"
    ],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o03",
    "group": "optics",
    "name": "PROMYN S10 LR",
    "code": "L10-LC",
    "sku": "DEMO-O03",
    "price": 189000,
    "available": true,
    "props": {
      "Швидкість": "10 Гбіт/с",
      "Роз’єм": "LC duplex",
      "Дальність": "10 км",
      "Форм-фактор": "SFP+",
      "Волокно": "Одномодове",
      "Моніторинг": "DDM"
    },
    "desc": "Швидше з’єднання для портів SFP+.",
    "compat": "Потрібен сумісний SFP+ порт 10 Гбіт/с. Роботу у звичайному SFP-порті не заявлено.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Лінк 10G · LC",
      "Лінк 10 LC",
      "Лінк 10G LC",
      "promyn",
      "Промін"
    ],
    "family": "PROMYN",
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "PROMYN S10 LR",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 10,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 10,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 189000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o04",
    "sku": "DEMO-O04",
    "group": "optics",
    "code": "O04",
    "price": 169000,
    "available": true,
    "props": {
      "Швидкість": "10 Гбіт/с",
      "Роз’єм": "LC duplex",
      "Дальність": "0,3 км",
      "Форм-фактор": "SFP+",
      "Волокно": "Багатомодове OM3",
      "Моніторинг": "DDM",
      "Довжина хвилі": "850 нм"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "PROMYN S10 SR",
    "family": "PROMYN",
    "aliases": [
      "promyn",
      "Промін"
    ],
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "PROMYN S10 SR",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 10,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 0.3,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 169000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o05",
    "sku": "DEMO-O05",
    "group": "optics",
    "code": "O05",
    "price": 99000,
    "available": true,
    "props": {
      "Швидкість": "1 Гбіт/с",
      "Роз’єм": "LC simplex",
      "Дальність": "20 км",
      "Форм-фактор": "SFP",
      "Волокно": "Одномодове",
      "Моніторинг": "DDM",
      "Довжина хвилі": "TX 1310 / RX 1550 нм"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "PROMYN S1 BX-U",
    "family": "PROMYN",
    "aliases": [
      "promyn",
      "Промін"
    ],
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "PROMYN S1 BX-U",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 20,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 99000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o06",
    "sku": "DEMO-O06",
    "group": "optics",
    "code": "O06",
    "price": 99000,
    "available": true,
    "props": {
      "Швидкість": "1 Гбіт/с",
      "Роз’єм": "LC simplex",
      "Дальність": "20 км",
      "Форм-фактор": "SFP",
      "Волокно": "Одномодове",
      "Моніторинг": "DDM",
      "Довжина хвилі": "TX 1550 / RX 1310 нм"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "PROMYN S1 BX-D",
    "family": "PROMYN",
    "aliases": [
      "promyn",
      "Промін"
    ],
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "PROMYN S1 BX-D",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 20,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 99000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "o07",
    "sku": "DEMO-O07",
    "group": "optics",
    "code": "O07",
    "price": 429000,
    "available": false,
    "props": {
      "Швидкість": "10 Гбіт/с",
      "Роз’єм": "LC duplex",
      "Дальність": "40 км",
      "Форм-фактор": "SFP+",
      "Волокно": "Одномодове",
      "Моніторинг": null,
      "Довжина хвилі": "1550 нм"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "PROMYN S10 ER",
    "family": "PROMYN",
    "aliases": [
      "promyn",
      "Промін"
    ],
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "PROMYN S10 ER",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 10,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 40,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 429000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Моніторинг"
    ],
    "tags": [
      "optics",
      "promyn"
    ]
  },
  {
    "id": "o08",
    "sku": "DEMO-O08",
    "group": "optics",
    "code": "O08",
    "price": 499000,
    "available": true,
    "props": {
      "Швидкість": "25 Гбіт/с",
      "Роз’єм": "LC duplex",
      "Дальність": "10 км",
      "Форм-фактор": "SFP28",
      "Волокно": "Одномодове",
      "Моніторинг": "DDM",
      "Довжина хвилі": "1310 нм"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "PROMYN S25 LR",
    "family": "PROMYN",
    "aliases": [
      "promyn",
      "Промін"
    ],
    "typeLabel": "Оптичні модулі",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "PROMYN S25 LR",
      "Оптичні модулі"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "optics-origin",
    "demoDocument": {
      "id": "o08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "speedGbps": {
        "value": 25,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "distanceKm": {
        "value": 10,
        "unit": "km",
        "derivedFrom": "Дальність"
      },
      "priceCents": {
        "value": 499000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "optics",
      "promyn",
      "in-stock"
    ]
  },
  {
    "id": "s01",
    "group": "switches",
    "name": "SVITRA K8",
    "code": "N8",
    "sku": "DEMO-S01",
    "price": 189000,
    "available": true,
    "props": {
      "LAN-порти": "8",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Ні",
      "Керування": "Некерований",
      "SFP-порти": "0",
      "Корпус": "Метал"
    },
    "desc": "Проста комутація невеликої мережі.",
    "compat": "Живлення кінцевих пристроїв через Ethernet не підтримується. Порти SFP відсутні.",
    "ng": false,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Контур 8",
      "Вузол 8",
      "svitra",
      "Світра"
    ],
    "family": "SVITRA",
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "SVITRA K8",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 189000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s02",
    "group": "switches",
    "name": "SVITRA K8 PoE",
    "code": "N8-P",
    "sku": "DEMO-S02",
    "price": 459000,
    "available": true,
    "props": {
      "LAN-порти": "8",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Так, 120 Вт",
      "Керування": "L2",
      "SFP-порти": "2",
      "Корпус": "Метал"
    },
    "desc": "Вісім портів із PoE та окремі оптичні підключення.",
    "compat": "Сумарний бюджет PoE — 120 Вт, до 30 Вт на порт. SFP-модулі купуються окремо.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Контур 8 PoE",
      "Вузол 8 PoE",
      "svitra",
      "Світра"
    ],
    "family": "SVITRA",
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "SVITRA K8 PoE",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 459000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s03",
    "group": "switches",
    "name": "SVITRA K24",
    "code": "N24",
    "sku": "DEMO-S03",
    "price": 649000,
    "available": true,
    "props": {
      "LAN-порти": "24",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Ні",
      "Керування": "L2",
      "SFP-порти": "2",
      "Корпус": "Метал"
    },
    "desc": "Керований комутатор для мережі з більшою кількістю точок.",
    "compat": "24 мідні та 2 окремі оптичні порти. PoE немає; модулі SFP не входять у комплект.",
    "ng": true,
    "unit": "шт.",
    "revision": "D1",
    "aliases": [
      "Контур 24",
      "Вузол 24",
      "svitra",
      "Світра"
    ],
    "family": "SVITRA",
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "SVITRA K24",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 24,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 649000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s04",
    "sku": "DEMO-S04",
    "group": "switches",
    "code": "S04",
    "price": 99000,
    "available": true,
    "props": {
      "LAN-порти": "5",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Ні",
      "Керування": "Некерований",
      "SFP-порти": "0",
      "Корпус": "Метал"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "SVITRA K5",
    "family": "SVITRA",
    "aliases": [
      "svitra",
      "Світра"
    ],
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "SVITRA K5",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 5,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 99000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s05",
    "sku": "DEMO-S05",
    "group": "switches",
    "code": "S05",
    "price": 419000,
    "available": true,
    "props": {
      "LAN-порти": "16",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Ні",
      "Керування": "L2",
      "SFP-порти": "2",
      "Корпус": "Метал"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "SVITRA K16",
    "family": "SVITRA",
    "aliases": [
      "svitra",
      "Світра"
    ],
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "SVITRA K16",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 16,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 419000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s06",
    "sku": "DEMO-S06",
    "group": "switches",
    "code": "S06",
    "price": 1199000,
    "available": true,
    "props": {
      "LAN-порти": "24",
      "Швидкість": "1 Гбіт/с",
      "PoE": "Так, 250 Вт",
      "Керування": "L2",
      "SFP-порти": "2",
      "Корпус": "Метал"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "SVITRA K24 PoE",
    "family": "SVITRA",
    "aliases": [
      "svitra",
      "Світра"
    ],
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "SVITRA K24 PoE",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 24,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": null,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 1199000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s07",
    "sku": "DEMO-S07",
    "group": "switches",
    "code": "S07",
    "price": 729000,
    "available": true,
    "props": {
      "LAN-порти": "8",
      "Швидкість": "2,5 Гбіт/с",
      "PoE": "Ні",
      "Керування": "L2",
      "SFP-порти": "0",
      "SFP+-порти": "2",
      "Корпус": "Метал"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "SVITRA K8 Multi",
    "family": "SVITRA",
    "aliases": [
      "svitra",
      "Світра"
    ],
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "SVITRA K8 Multi",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 729000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra",
      "in-stock"
    ]
  },
  {
    "id": "s08",
    "sku": "DEMO-S08",
    "group": "switches",
    "code": "S08",
    "price": 1899000,
    "available": false,
    "props": {
      "LAN-порти": "16",
      "Швидкість": "2,5 Гбіт/с",
      "PoE": "Так, 180 Вт",
      "Керування": "L2",
      "SFP-порти": "0",
      "SFP+-порти": "2",
      "Корпус": "Метал"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "SVITRA K16 Multi",
    "family": "SVITRA",
    "aliases": [
      "svitra",
      "Світра"
    ],
    "typeLabel": "Мережеві комутатори",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "SVITRA K16 Multi",
      "Мережеві комутатори"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "switches-origin",
    "demoDocument": {
      "id": "s08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "lanPorts": {
        "value": 16,
        "unit": "count",
        "derivedFrom": "LAN-порти"
      },
      "speedGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "sfpPorts": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "SFP-порти"
      },
      "sfpPlusPorts": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "SFP+-порти"
      },
      "priceCents": {
        "value": 1899000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "switches",
      "svitra"
    ]
  },
  {
    "id": "c01",
    "group": "cable",
    "name": "STRUNEX F6 Core 100",
    "code": "CU-IN",
    "sku": "DEMO-C01",
    "price": 219000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 6",
      "Пари": "4",
      "Оболонка": "LSZH",
      "Довжина бухти": "100 м"
    },
    "desc": "Мідний кабель для внутрішнього прокладання.",
    "compat": "Продається цілою бухтою 100 м. Одна одиниця в кошику — одна бухта, не один метр.",
    "ng": true,
    "unit": "бухта 100 м",
    "revision": "D1",
    "aliases": [
      "Траса Cu · приміщення",
      "Лінія Cu Indoor",
      "Траса Cu Indoor 100",
      "strunex",
      "Струнекс"
    ],
    "family": "STRUNEX",
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "STRUNEX F6 Core 100",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 100,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 100,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 219000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "in-stock"
    ]
  },
  {
    "id": "c02",
    "group": "cable",
    "name": "STRUNEX F6 Field 100",
    "code": "CU-OUT",
    "sku": "DEMO-C02",
    "price": 259000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "Надворі",
      "Категорія": "Cat 6",
      "Пари": "4",
      "Оболонка": "PE",
      "Довжина бухти": "100 м"
    },
    "desc": "Мідний кабель із зовнішньою оболонкою PE.",
    "compat": "Одна одиниця — бухта 100 м. Зовнішня оболонка PE не означає відповідність вимогам до внутрішньої пожежної безпеки.",
    "ng": true,
    "unit": "бухта 100 м",
    "revision": "D1",
    "aliases": [
      "Траса Cu · вулиця",
      "Лінія Cu Outdoor",
      "Траса Cu Outdoor 100",
      "strunex",
      "Струнекс"
    ],
    "family": "STRUNEX",
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "STRUNEX F6 Field 100",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 100,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 100,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 259000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "outdoor",
      "in-stock"
    ]
  },
  {
    "id": "c03",
    "group": "cable",
    "name": "STRUNEX F5 Alloy 100",
    "code": "CCA-IN",
    "sku": "DEMO-C03",
    "price": 119000,
    "available": false,
    "props": {
      "Матеріал": "CCA",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 5e",
      "Пари": "4",
      "Оболонка": "PVC",
      "Довжина бухти": "100 м"
    },
    "desc": "Оміднений алюміній для демонстрації відмінностей матеріалу.",
    "compat": "CCA — не суцільна мідь. Придатність для PoE не заявлено. Одна одиниця — бухта 100 м.",
    "ng": false,
    "unit": "бухта 100 м",
    "revision": "D1",
    "aliases": [
      "Траса CCA · приміщення",
      "Лінія CCA Indoor",
      "Траса CCA Indoor 100",
      "strunex",
      "Струнекс"
    ],
    "family": "STRUNEX",
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": true,
    "titleLines": [
      "STRUNEX F5 Alloy 100",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 100,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 100,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 119000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex"
    ]
  },
  {
    "id": "c04",
    "sku": "DEMO-C04",
    "group": "cable",
    "code": "C04",
    "price": 519000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 6",
      "Пари": "4",
      "Оболонка": "LSZH",
      "Довжина бухти": "305 м",
      "Екранування": "U/UTP"
    },
    "ng": true,
    "revision": "D1",
    "unit": "бухта 305 м",
    "name": "STRUNEX F6 Core 305",
    "family": "STRUNEX",
    "aliases": [
      "strunex",
      "Струнекс"
    ],
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "STRUNEX F6 Core 305",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 305,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 305,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 519000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "in-stock"
    ]
  },
  {
    "id": "c05",
    "sku": "DEMO-C05",
    "group": "cable",
    "code": "C05",
    "price": 359000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 6A",
      "Пари": "4",
      "Оболонка": "LSZH",
      "Довжина бухти": "100 м",
      "Екранування": "F/UTP"
    },
    "ng": true,
    "revision": "D1",
    "unit": "бухта 100 м",
    "name": "STRUNEX F6A Core 100",
    "family": "STRUNEX",
    "aliases": [
      "strunex",
      "Струнекс"
    ],
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "STRUNEX F6A Core 100",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 100,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 100,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 359000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "in-stock"
    ]
  },
  {
    "id": "c06",
    "sku": "DEMO-C06",
    "group": "cable",
    "code": "C06",
    "price": 999000,
    "available": false,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "Надворі",
      "Категорія": "Cat 6A",
      "Пари": "4",
      "Оболонка": "PE",
      "Довжина бухти": "305 м",
      "Екранування": "F/UTP"
    },
    "ng": true,
    "revision": "D1",
    "unit": "бухта 305 м",
    "name": "STRUNEX F6A Field 305",
    "family": "STRUNEX",
    "aliases": [
      "strunex",
      "Струнекс"
    ],
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "STRUNEX F6A Field 305",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 305,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 305,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 999000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "outdoor"
    ]
  },
  {
    "id": "c07",
    "sku": "DEMO-C07",
    "group": "cable",
    "code": "C07",
    "price": 399000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 5e",
      "Пари": "4",
      "Оболонка": "PVC",
      "Довжина бухти": "305 м",
      "Екранування": "U/UTP"
    },
    "ng": true,
    "revision": "D1",
    "unit": "бухта 305 м",
    "name": "STRUNEX F5 Core 305",
    "family": "STRUNEX",
    "aliases": [
      "strunex",
      "Струнекс"
    ],
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "STRUNEX F5 Core 305",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 305,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 305,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 399000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "in-stock"
    ]
  },
  {
    "id": "c08",
    "sku": "DEMO-C08",
    "group": "cable",
    "code": "C08",
    "price": 289000,
    "available": true,
    "props": {
      "Матеріал": "Cu",
      "Застосування": "У приміщенні",
      "Категорія": "Cat 6",
      "Пари": "4",
      "Оболонка": "LSZH",
      "Довжина бухти": "100 м",
      "Екранування": "F/UTP"
    },
    "ng": true,
    "revision": "D1",
    "unit": "бухта 100 м",
    "name": "STRUNEX F6 Shield 100",
    "family": "STRUNEX",
    "aliases": [
      "strunex",
      "Струнекс"
    ],
    "typeLabel": "Кабель для мереж",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "STRUNEX F6 Shield 100",
      "Кабель для мереж"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "cable-origin",
    "demoDocument": {
      "id": "c08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "reel",
      "lengthM": 100,
      "integerOnly": true
    },
    "numericFacets": {
      "pairs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Пари"
      },
      "reelM": {
        "value": 100,
        "unit": "m",
        "derivedFrom": "Довжина бухти"
      },
      "priceCents": {
        "value": 289000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "cable",
      "strunex",
      "copper",
      "in-stock"
    ]
  },
  {
    "id": "a01",
    "sku": "DEMO-A01",
    "group": "wifi",
    "code": "A01",
    "price": 219000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "1 Гбіт/с",
      "Живлення PoE": "802.3af",
      "Монтаж": "Настільне",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "10 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Mini",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Mini",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 10,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 219000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a02",
    "sku": "DEMO-A02",
    "group": "wifi",
    "code": "A02",
    "price": 399000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "1 Гбіт/с",
      "Живлення PoE": "802.3at",
      "Монтаж": "Стельове",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "18 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Ceiling",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Ceiling",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 18,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 399000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a03",
    "sku": "DEMO-A03",
    "group": "wifi",
    "code": "A03",
    "price": 419000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "1 Гбіт/с",
      "Живлення PoE": "802.3at",
      "Монтаж": "Настінне",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "20 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Wall",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Wall",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 20,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 419000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a04",
    "sku": "DEMO-A04",
    "group": "wifi",
    "code": "A04",
    "price": 599000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "1 Гбіт/с",
      "Живлення PoE": "802.3at",
      "Монтаж": "На кронштейні",
      "Середовище": "Надворі",
      "Гранична споживана потужність": "22 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Courtyard",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Courtyard",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 22,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 599000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "outdoor",
      "in-stock"
    ]
  },
  {
    "id": "a05",
    "sku": "DEMO-A05",
    "group": "wifi",
    "code": "A05",
    "price": 479000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "1 Гбіт/с",
      "Живлення PoE": "802.3at",
      "Монтаж": "Настільне",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "18 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Mesh",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Mesh",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 18,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 479000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a06",
    "sku": "DEMO-A06",
    "group": "wifi",
    "code": "A06",
    "price": 639000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6",
      "Діапазони": "2,4 / 5 ГГц",
      "Ethernet": "2,5 Гбіт/с",
      "Живлення PoE": "802.3at",
      "Монтаж": "Стельове",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "25 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6 Studio",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6 Studio",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 25,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 639000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a07",
    "sku": "DEMO-A07",
    "group": "wifi",
    "code": "A07",
    "price": 999000,
    "available": true,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6E",
      "Діапазони": "2,4 / 5 / 6 ГГц",
      "Ethernet": "2,5 Гбіт/с",
      "Живлення PoE": "802.3bt",
      "Монтаж": "Стельове",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "35 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6E Lab",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6E Lab",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 35,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 999000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx",
      "in-stock"
    ]
  },
  {
    "id": "a08",
    "sku": "DEMO-A08",
    "group": "wifi",
    "code": "A08",
    "price": 1049000,
    "available": false,
    "props": {
      "Стандарт Wi-Fi": "Wi-Fi 6E",
      "Діапазони": "2,4 / 5 / 6 ГГц",
      "Ethernet": "2,5 Гбіт/с",
      "Живлення PoE": "802.3bt",
      "Монтаж": "Настінне",
      "Середовище": "Приміщення",
      "Гранична споживана потужність": "35 Вт"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "ZORYX H6E Loft",
    "family": "ZORYX",
    "aliases": [
      "zoryx",
      "Зорікс"
    ],
    "typeLabel": "Точки доступу Wi-Fi",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "ZORYX H6E Loft",
      "Точки доступу Wi-Fi"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "wifi-origin",
    "demoDocument": {
      "id": "a08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "ethernetGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Ethernet"
      },
      "powerInputMaxW": {
        "value": 35,
        "unit": "W",
        "derivedFrom": "Гранична споживана потужність"
      },
      "priceCents": {
        "value": 1049000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "wifi",
      "zoryx"
    ]
  },
  {
    "id": "p01",
    "sku": "DEMO-P01",
    "group": "splitters",
    "code": "P01",
    "price": 35000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×2",
      "Виконання": "Міні-корпус",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Оптичний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B2 Mini",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B2 Mini",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 35000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p02",
    "sku": "DEMO-P02",
    "group": "splitters",
    "code": "P02",
    "price": 45000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×4",
      "Виконання": "Міні-корпус",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Оптичний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B4 Mini",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B4 Mini",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 4,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 45000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p03",
    "sku": "DEMO-P03",
    "group": "splitters",
    "code": "P03",
    "price": 65000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×8",
      "Виконання": "Міні-корпус",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Оптичний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B8 Mini",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B8 Mini",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 65000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p04",
    "sku": "DEMO-P04",
    "group": "splitters",
    "code": "P04",
    "price": 79000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×8",
      "Виконання": "ABS",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Оптичний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B8 Case",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B8 Case",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 79000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p05",
    "sku": "DEMO-P05",
    "group": "splitters",
    "code": "P05",
    "price": 129000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×8",
      "Виконання": "Касета LGX",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Модульний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B8 Cassette",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B8 Cassette",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 8,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 129000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p06",
    "sku": "DEMO-P06",
    "group": "splitters",
    "code": "P06",
    "price": 109000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×16",
      "Виконання": "ABS",
      "Роз’єм": "SC/APC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Оптичний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B16 Case",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B16 Case",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 16,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 109000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p07",
    "sku": "DEMO-P07",
    "group": "splitters",
    "code": "P07",
    "price": 179000,
    "available": true,
    "props": {
      "Коефіцієнт ділення": "1×16",
      "Виконання": "Касета LGX",
      "Роз’єм": "SC/UPC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Модульний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B16 Cassette",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B16 Cassette",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 16,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 179000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk",
      "in-stock"
    ]
  },
  {
    "id": "p08",
    "sku": "DEMO-P08",
    "group": "splitters",
    "code": "P08",
    "price": 299000,
    "available": false,
    "props": {
      "Коефіцієнт ділення": "1×32",
      "Виконання": "Касета LGX",
      "Роз’єм": "SC/APC",
      "Волокно": "Одномодове",
      "Довжини хвиль": "1260–1650 нм",
      "Внесені втрати": null,
      "Монтаж": "Модульний бокс"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "FIBRYK B32 Cassette",
    "family": "FIBRYK",
    "aliases": [
      "fibryk",
      "Фібрик"
    ],
    "typeLabel": "Оптичні дільники PLC",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "FIBRYK B32 Cassette",
      "Оптичні дільники PLC"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "splitters-origin",
    "demoDocument": {
      "id": "p08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "outputs": {
        "value": 32,
        "unit": "count",
        "derivedFrom": "Коефіцієнт ділення"
      },
      "priceCents": {
        "value": 299000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Внесені втрати"
    ],
    "tags": [
      "splitters",
      "fibryk"
    ]
  },
  {
    "id": "m01",
    "sku": "DEMO-M01",
    "group": "meters",
    "code": "M01",
    "price": 149000,
    "available": true,
    "props": {
      "Діапазон": "−70…+10 dBm",
      "Адаптери": "SC / FC",
      "Експорт": "Немає",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "0",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P1 Pocket",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P1 Pocket",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 149000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m02",
    "sku": "DEMO-M02",
    "group": "meters",
    "code": "M02",
    "price": 199000,
    "available": true,
    "props": {
      "Діапазон": "−50…+26 dBm",
      "Адаптери": "SC / FC",
      "Експорт": "Немає",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "0",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P1 Wide",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P1 Wide",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 0,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 199000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m03",
    "sku": "DEMO-M03",
    "group": "meters",
    "code": "M03",
    "price": 269000,
    "available": true,
    "props": {
      "Діапазон": "−70…+10 dBm",
      "Адаптери": "SC / FC / ST",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "100",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P2 Field",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P2 Field",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 100,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 269000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m04",
    "sku": "DEMO-M04",
    "group": "meters",
    "code": "M04",
    "price": 319000,
    "available": true,
    "props": {
      "Діапазон": "−50…+26 dBm",
      "Адаптери": "SC / FC / ST",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "100",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P2 Wide",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P2 Wide",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 100,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 319000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m05",
    "sku": "DEMO-M05",
    "group": "meters",
    "code": "M05",
    "price": 419000,
    "available": true,
    "props": {
      "Діапазон": "−70…+10 dBm",
      "Адаптери": "SC / FC / ST",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "500",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P3 Trace",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P3 Trace",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 500,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 419000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m06",
    "sku": "DEMO-M06",
    "group": "meters",
    "code": "M06",
    "price": 449000,
    "available": true,
    "props": {
      "Діапазон": "−50…+26 dBm",
      "Адаптери": "SC / FC / ST",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "500",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P3 Wide",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P3 Wide",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 500,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 449000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "m07",
    "sku": "DEMO-M07",
    "group": "meters",
    "code": "M07",
    "price": 549000,
    "available": false,
    "props": {
      "Діапазон": "−70…+10 dBm",
      "Адаптери": "SC / FC",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "1000",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P4 Bench",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P4 Bench",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 1000,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 549000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk"
    ]
  },
  {
    "id": "m08",
    "sku": "DEMO-M08",
    "group": "meters",
    "code": "M08",
    "price": 599000,
    "available": true,
    "props": {
      "Діапазон": "−50…+26 dBm",
      "Адаптери": "SC / FC",
      "Експорт": "USB-C",
      "Довжини хвиль": "850 / 1300 / 1310 / 1490 / 1550 / 1625 нм",
      "Пам’ять вимірів": "1000",
      "Похибка": null,
      "Клас приладу": "Вимірювач оптичної потужності"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "KVANTYK P4 Link",
    "family": "KVANTYK",
    "aliases": [
      "kvantyk",
      "Квантик"
    ],
    "typeLabel": "Вимірювачі оптичної потужності",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "KVANTYK P4 Link",
      "Вимірювачі оптичної потужності"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "meters-origin",
    "demoDocument": {
      "id": "m08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "memorySamples": {
        "value": 1000,
        "unit": "count",
        "derivedFrom": "Пам’ять вимірів"
      },
      "priceCents": {
        "value": 599000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [
      "Похибка"
    ],
    "tags": [
      "meters",
      "kvantyk",
      "in-stock"
    ]
  },
  {
    "id": "i01",
    "sku": "DEMO-I01",
    "group": "injectors",
    "code": "I01",
    "price": 49000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3af",
      "Сумарна вихідна потужність": "15,4 Вт",
      "Потужність на порт": "15,4 Вт",
      "Швидкість": "1 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A15",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A15",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i01-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 15.4,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 15.4,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 49000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i02",
    "sku": "DEMO-I02",
    "group": "injectors",
    "code": "I02",
    "price": 89000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3at",
      "Сумарна вихідна потужність": "30 Вт",
      "Потужність на порт": "30 Вт",
      "Швидкість": "1 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A30",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A30",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i02-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 30,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 30,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 89000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i03",
    "sku": "DEMO-I03",
    "group": "injectors",
    "code": "I03",
    "price": 169000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3bt",
      "Сумарна вихідна потужність": "60 Вт",
      "Потужність на порт": "60 Вт",
      "Швидкість": "1 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A60",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A60",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i03-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 169000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i04",
    "sku": "DEMO-I04",
    "group": "injectors",
    "code": "I04",
    "price": 239000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3bt",
      "Сумарна вихідна потужність": "90 Вт",
      "Потужність на порт": "90 Вт",
      "Швидкість": "1 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A90",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A90",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i04-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 90,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 90,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 239000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i05",
    "sku": "DEMO-I05",
    "group": "injectors",
    "code": "I05",
    "price": 139000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3at",
      "Сумарна вихідна потужність": "30 Вт",
      "Потужність на порт": "30 Вт",
      "Швидкість": "2,5 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A30 Multi",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A30 Multi",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i05-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 30,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 30,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 139000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i06",
    "sku": "DEMO-I06",
    "group": "injectors",
    "code": "I06",
    "price": 239000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3bt",
      "Сумарна вихідна потужність": "60 Вт",
      "Потужність на порт": "60 Вт",
      "Швидкість": "2,5 Гбіт/с",
      "PoE-порти": "1",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A60 Multi",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A60 Multi",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i06-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 1,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 239000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i07",
    "sku": "DEMO-I07",
    "group": "injectors",
    "code": "I07",
    "price": 159000,
    "available": true,
    "props": {
      "PoE": "IEEE 802.3at",
      "Сумарна вихідна потужність": "60 Вт",
      "Потужність на порт": "30 Вт",
      "Швидкість": "1 Гбіт/с",
      "PoE-порти": "2",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A30 Dual",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A30 Dual",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i07-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "available",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 30,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 1,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 159000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn",
      "in-stock"
    ]
  },
  {
    "id": "i08",
    "sku": "DEMO-I08",
    "group": "injectors",
    "code": "I08",
    "price": 369000,
    "available": false,
    "props": {
      "PoE": "IEEE 802.3bt",
      "Сумарна вихідна потужність": "120 Вт",
      "Потужність на порт": "60 Вт",
      "Швидкість": "2,5 Гбіт/с",
      "PoE-порти": "2",
      "Тип": "Активне узгодження",
      "Живлення": "100–240 В AC"
    },
    "ng": true,
    "revision": "D1",
    "unit": "шт.",
    "name": "MODULYN A60 Dual",
    "family": "MODULYN",
    "aliases": [
      "modulyn",
      "Модулин"
    ],
    "typeLabel": "Інжектори PoE",
    "isDemo": true,
    "sourceKind": "synthetic-ui-fixture",
    "legacyId": false,
    "titleLines": [
      "MODULYN A60 Dual",
      "Інжектори PoE"
    ],
    "sourceNote": "Умовна модель: не реальний товар, не перевірена характеристика обладнання.",
    "storyId": "injectors-origin",
    "demoDocument": {
      "id": "i08-D1",
      "revision": "D1",
      "type": "Демонстраційна специфікація",
      "language": "uk",
      "source": "generate_from_catalog",
      "containsCertification": false
    },
    "desc": "Демонстраційне виконання для зіставлення параметрів, одиниці продажу й подальшої дії.",
    "compat": "Перед реальним підключенням потрібні паспорт і перевірка повного набору умов. Умовні значення не є технічною рекомендацією.",
    "availabilityState": "unavailable",
    "unitDefinition": {
      "kind": "piece",
      "integerOnly": true
    },
    "numericFacets": {
      "budgetW": {
        "value": 120,
        "unit": "W",
        "derivedFrom": "Сумарна вихідна потужність"
      },
      "portMaxW": {
        "value": 60,
        "unit": "W",
        "derivedFrom": "Потужність на порт"
      },
      "speedGbps": {
        "value": 2.5,
        "unit": "Gbps",
        "derivedFrom": "Швидкість"
      },
      "ports": {
        "value": 2,
        "unit": "count",
        "derivedFrom": "PoE-порти"
      },
      "priceCents": {
        "value": 369000,
        "unit": "UAH_cent",
        "derivedFrom": "price"
      }
    },
    "knownMissingFields": [],
    "tags": [
      "injectors",
      "modulyn"
    ]
  }
];
export const products=[...coreProducts.map(p=>({...p,manufacturer:p.family})),...expandedProducts];
// Keep f0/f1 meanings stable so existing saved URLs remain valid.
groups.ups.filters.push('Роз’єм DC');
groups.optics.filters.push('Форм-фактор','Волокно');
groups.switches.filters.push('Керування','Швидкість');
groups.cable.filters.push('Категорія','Довжина бухти','Оболонка');
groups.wifi.filters.push('Середовище','Живлення PoE');
groups.splitters.filters.push('Виконання');
groups.meters.filters.push('Експорт');
groups.injectors.filters.push('PoE-порти');
for(const [group,keys] of Object.entries({optics:['Температура'],switches:['Бюджет PoE','Монтаж','Охолодження'],cable:['Екранування','Діаметр провідника'],wifi:['Потоки MIMO']}))groups[group].keys.push(...keys);
for(const g of Object.values(groups))g.filters=[...new Set(g.filters)];
groups.splitters.numericFacetDefinitions=[['outputs','Кількість виходів','count']];
groups.wifi.icon='wifi';groups.splitters.icon='splitter';groups.meters.icon='meter';groups.injectors.icon='plug';
export const byId=id=>products.find(p=>p.id===id);
export const display=v=>v===null||v===undefined?'Не уточнено':String(v);
export const money=cents=>new Intl.NumberFormat('uk-UA',{maximumFractionDigits:2}).format(cents/100)+' грн';
export const highlights={
  "ups": [
    "Потужність",
    "Запас енергії",
    "Виходи"
  ],
  "optics": [
    "Швидкість",
    "Роз’єм",
    "Дальність"
  ],
  "switches": [
    "LAN-порти",
    "Керування",
    "PoE"
  ],
  "cable": [
    "Матеріал",
    "Категорія",
    "Застосування"
  ],
  "wifi": [
    "Стандарт Wi-Fi",
    "Ethernet",
    "Середовище"
  ],
  "splitters": [
    "Коефіцієнт ділення",
    "Роз’єм",
    "Внесені втрати"
  ],
  "meters": [
    "Діапазон",
    "Адаптери",
    "Експорт"
  ],
  "injectors": [
    "PoE",
    "Сумарна вихідна потужність",
    "Швидкість"
  ]
};
export const artwork={ups:'mini-ups',optics:'optical-transceiver',switches:'network-switch',cable:'network-cable',wifi:'network-switch',splitters:'optical-transceiver',meters:'optical-transceiver',injectors:'mini-ups'};
export const numericValue=(p,key)=>{const value=p?.numericFacets?.[key]?.value;return typeof value==='number'&&Number.isFinite(value)?value:null;};
export function reelLength(p){
 const value=p?.unitDefinition?.lengthM;
 if(typeof value==='number'&&Number.isFinite(value)&&value>0)return value;
 const match=String(p?.unit||'').match(/(\d+(?:[.,]\d+)?)\s*м(?:\s|$)/u);
 return match?Number(match[1].replace(',','.')):null;
}

