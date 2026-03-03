"""
Load sample Saudi laws into the database for testing
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Sample Saudi law data
SAMPLE_LAWS = [
    {
        "title_ar": "النظام الأساسي للحكم",
        "title_en": "Basic Law of Governance",
        "category": "Constitutional",
        "content_ar": """النظام الأساسي للحكم
صدر بالأمر الملكي رقم (أ/90) وتاريخ 27/8/1412هـ

المادة الأولى:
المملكة العربية السعودية، دولة عربية إسلامية، ذات سيادة تامة؛ دينها الإسلام، ودستورها كتاب الله تعالى وسنة رسوله صلى الله عليه وسلم، ولغتها هي اللغة العربية، وعاصمتها مدينة الرياض.

المادة الثانية:
عيدا الدولة، هما: عيد الفطر وعيد الأضحى، وتقويمها هو التقويم الهجري.

المادة الثالثة:
يكون علم الدولة على النحو الآتي:
أ - لونه أخضر.
ب - عرضه يساوي ثلثي طوله.
ج - تتوسطه كلمة (لا إله إلا الله محمد رسول الله)، تحتها سيف مسلول، تكون قبضته باتجاه سارية العلم.
د - ولا ينكس علم الدولة أبداً.

المادة الرابعة:
شعار الدولة هو: سيفان متقاطعان، ونخلة في وسط الفراغ الأعلى بينهما.""",
        "content_en": """Basic Law of Governance
Issued by Royal Order No. (A/90) dated 27/8/1412 H

Article 1:
The Kingdom of Saudi Arabia is a sovereign Arab Islamic state with Islam as its religion; God's Book and the Sunnah of His Messenger, God's prayers and peace be upon him, are its constitution, Arabic is its language and Riyadh is its capital.

Article 2:
The state's public holidays are Id al-Fitr and Id al-Adha. Its calendar is the Hegira calendar.

Article 3:
The state's flag shall be as follows:
a. Its color is green.
b. Its width equals two-thirds of its length.
c. The words "There is no god but God, and Muhammad is His Messenger" are inscribed in the center with a drawn sword under it.
d. The state flag shall never be lowered.

Article 4:
The state's emblem consists of two crossed swords with a palm tree in the upper space between them.""",
        "law_number": "A/90",
        "issue_date": "1991-03-01",
        "hijri_date": "1412-08-27"
    },
    {
        "title_ar": "نظام مكافحة جرائم الإرهاب وتمويله",
        "title_en": "Law of Terrorism Crimes and Financing",
        "category": "Criminal Law",
        "content_ar": """نظام مكافحة جرائم الإرهاب وتمويله
صدر بالمرسوم الملكي رقم (م / 16) وتاريخ 24/2/1435هـ

المادة الأولى:
تُقصد بالعبارات والألفاظ الآتية -أينما وردت في هذا النظام- المعاني المُبينة أمام كل منها، ما لم يقتض السياق خلاف ذلك:
1- الإرهاب: كل فعل أو تهديد بفعل، أياً كانت بواعثه أو أغراضه، يُنَفَّذ تحقيقاً لمشروع فردي أو جماعي إجرامي، بشكل مباشر أو غير مباشر، يقصد به الإخلال بالنظام العام، أو زعزعة أمن المجتمع أو استقرار الدولة، أو تعريض سلامتها أو مصالحها الوطنية للخطر، أو إلحاق الضرر بالمؤسسات أو المقرات الدبلوماسية، أو المنشآت الحكومية، أو الخدمات العامة، أو العبث بالأملاك العامة، أو بالموارد الطبيعية.

المادة الثانية:
يُعاقب كل من يرتكب جريمة إرهابية، أو يخطط أو يمول أو يُحرض عليها، بعقوبة تصل إلى عشرين سنة، أو الإعدام في حالات استثنائية.""",
        "content_en": """Law of Terrorism Crimes and Financing
Issued by Royal Decree No. (M/16) dated 24/2/1435H

Article 1:
The following terms and expressions wherever mentioned in this Law shall have the meanings indicated opposite each unless the context indicates otherwise:
1- Terrorism: Any act or threat thereof, whatever its motives or purposes, which is carried out in implementation of an individual or collective criminal project, directly or indirectly, aimed at disturbing public order, or destabilizing the security or stability of the State, or exposing its safety or national interests to danger, or causing damage to diplomatic missions, or governmental facilities, or public services, or tampering with public property, or natural resources.

Article 2:
Any person who commits a terrorist crime, plans, finances or incites it, shall be punished with a penalty of up to twenty years, or death in exceptional cases.""",
        "law_number": "M/16",
        "issue_date": "2014-01-26",
        "hijri_date": "1435-02-24"
    },
    {
        "title_ar": "نظام العمل",
        "title_en": "Labor Law",
        "category": "Labor & Employment",
        "content_ar": """نظام العمل
صدر بالمرسوم الملكي رقم (م/51) وتاريخ 23/8/1426هـ

المادة الأولى:
يقصد بالألفاظ والعبارات الآتية المعاني الموضحة أمام كل منها، ما لم يقتض السياق معنى آخر:
1- العامل: كل شخص طبيعي يعمل لمصلحة صاحب عمل وتحت إدارته أو إشرافه مقابل أجر.
2- صاحب العمل: كل شخص طبيعي أو اعتباري يشغل عاملاً أو أكثر مقابل أجر.
3- الأجر: كل ما يعطى للعامل مقابل عمله بموجب عقد عمل مكتوب أو غير مكتوب، نقداً أو عيناً.

المادة الثانية:
يجب أن تكون ساعات العمل الفعلية ثماني ساعات في اليوم، إذا اعتمد صاحب العمل المعيار اليومي، وثماني وأربعين ساعة في الأسبوع، إذا اعتمد المعيار الأسبوعي.

المادة الثالثة:
للعامل الحق في إجازة سنوية لا تقل مدتها عن واحد وعشرين يوماً، تزاد إلى مدة ثلاثين يوماً إذا أمضى العامل خمس سنوات متصلة في خدمة صاحب العمل.""",
        "content_en": """Labor Law
Issued by Royal Decree No. (M/51) dated 23/8/1426H

Article 1:
The following words and phrases shall have the meanings set forth opposite each of them unless the context requires otherwise:
1- Worker: Any natural person who works for an employer and is under his management or supervision in return for a wage.
2- Employer: Any natural or juridical person who employs one or more workers in return for a wage.
3- Wage: Everything that is given to a worker in return for his work under a written or unwritten work contract, in cash or in kind.

Article 2:
The actual working hours shall be eight hours per day, if the employer adopts the daily standard, and forty-eight hours per week, if the weekly standard is adopted.

Article 3:
The worker is entitled to an annual leave of not less than twenty-one days, which shall be increased to thirty days if the worker has completed five consecutive years in the service of the employer.""",
        "law_number": "M/51",
        "issue_date": "2005-09-27",
        "hijri_date": "1426-08-23"
    }
]


def main():
    """Load sample laws into the database"""

    # Initialize Supabase client
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return

    supabase = create_client(supabase_url, supabase_key)

    print("=" * 80)
    print("Loading Sample Saudi Laws")
    print("=" * 80)

    # Insert sample laws
    for law in SAMPLE_LAWS:
        try:
            print(f"\n📖 Inserting: {law['title_en']}")

            # Map to correct schema
            law_data = {
                'name_ar': law['title_ar'],
                'name_en': law['title_en'],
                'law_number': law['law_number'],
                'full_text_ar': law['content_ar'],
                'full_text_en': law['content_en'],
                'publication_date': law['issue_date'],
                'url': f"https://laws.boe.gov.sa/BoeLaws/Laws/{law['law_number']}",
                'metadata': {
                    'category': law['category'],
                    'hijri_date': law['hijri_date']
                }
            }

            result = supabase.table('laws').insert(law_data).execute()
            print(f"✅ Successfully inserted: {law['title_en']}")
        except Exception as e:
            print(f"❌ Error inserting {law['title_en']}: {e}")

    print("\n" + "=" * 80)
    print("✅ Sample data loaded successfully!")
    print("=" * 80)

    # Check how many laws are in the database
    try:
        count_result = supabase.table('laws').select('id', count='exact').execute()
        print(f"\n📊 Total laws in database: {count_result.count}")
    except Exception as e:
        print(f"❌ Error counting laws: {e}")


if __name__ == "__main__":
    main()
