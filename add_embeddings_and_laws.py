#!/usr/bin/env python3
"""
Add embeddings for existing laws and insert new sample laws
"""

import time
from openai import OpenAI
from supabase import create_client

def load_env():
    env = {}
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                env[key] = val
    return env

# Additional sample laws
NEW_LAWS = [
    {
        "name_ar": "نظام الشركات",
        "law_number": "M/132",
        "full_text_ar": """نظام الشركات: يجوز تأسيس أي من أنواع الشركات من قبل شخص أو أكثر. الشركة ذات المسؤولية المحدودة يجب أن يكون رأس مالها مقسماً إلى حصص متساوية القيمة. الشركة المساهمة يقسم رأس مالها إلى أسهم متساوية القيمة وقابلة للتداول. يجب على الشركات الالتزام بمتطلبات الإفصاح والشفافية."""
    },
    {
        "name_ar": "نظام الجرائم المعلوماتية",
        "law_number": "M/17",
        "full_text_ar": """نظام مكافحة الجرائم المعلوماتية: يعاقب بالسجن مدة لا تزيد على سنة وبغرامة لا تزيد على 500,000 ريال كل من يدخل بشكل غير مشروع لإلغاء أو حذف أو تدمير أو تسريب بيانات خاصة. يعاقب بالسجن مدة لا تزيد على ثلاث سنوات وبغرامة لا تزيد على مليوني ريال كل من ينتج أو يعد أو يرسل ما من شأنه المساس بالنظام العام أو القيم الدينية."""
    },
    {
        "name_ar": "نظام المرور",
        "law_number": "M/85",
        "full_text_ar": """نظام المرور: لا يجوز قيادة أي مركبة آلية على الطريق العام إلا بعد الحصول على رخصة قيادة. يجب التقيد بالسرعة المحددة وعدم تجاوزها. يعاقب من يقود مركبة تحت تأثير المسكرات أو المخدرات بالسجن مدة لا تقل عن شهر ولا تزيد على سنة وبغرامة من 5,000 إلى 10,000 ريال."""
    },
    {
        "name_ar": "نظام حماية المستهلك",
        "law_number": "M/24",
        "full_text_ar": """نظام حماية المستهلك: للمستهلك الحق في الحصول على معلومات واضحة ودقيقة عن المنتجات والخدمات. للمستهلك الحق في استرجاع أو استبدال المنتج خلال 7 أيام من تاريخ الشراء في حال وجود عيب. يحظر على المورد الإعلان عن منتج بطريقة خادعة أو مضللة. يحق للمستهلك تقديم شكوى لدى وزارة التجارة."""
    },
    {
        "name_ar": "نظام الإجراءات الجزائية",
        "law_number": "M/2",
        "full_text_ar": """نظام الإجراءات الجزائية: لا يجوز القبض على أي إنسان أو تفتيشه أو توقيفه أو سجنه إلا في الأحوال المنصوص عليها نظاماً. التوقيف لا يكون إلا في الأماكن المخصصة له. المتهم بريء حتى تثبت إدانته بحكم نهائي. للمتهم الحق في الاستعانة بوكيل أو محام للدفاع عنه في مرحلتي التحقيق والمحاكمة."""
    },
    {
        "name_ar": "نظام الضمان الاجتماعي",
        "law_number": "M/32",
        "full_text_ar": """نظام الضمان الاجتماعي: يهدف إلى توفير الحماية الاجتماعية اللازمة للأسر الأشد حاجة. يشمل المعاش المستحق تكاليف المعيشة والصحة والتعليم والسكن. تصرف المعاشات شهرياً للمستحقين. يشترط أن يكون المستفيد سعودي الجنسية مقيماً إقامة دائمة في المملكة."""
    }
]

def main():
    print("=" * 80)
    print("🔄 Adding Embeddings & New Laws")
    print("=" * 80)

    env = load_env()
    supabase = create_client(env['SUPABASE_URL'], env['SUPABASE_SERVICE_ROLE_KEY'])
    openai_client = OpenAI(api_key=env['OPENAI_API_KEY'])

    # Step 1: Add embeddings for existing laws that don't have them
    print("\n📊 Step 1: Adding embeddings for existing laws...")

    existing_laws = supabase.table('laws').select('*').execute()

    for law in existing_laws.data:
        # Check if embedding exists
        emb_check = supabase.table('law_embeddings').select('id').eq('law_id', law['id']).execute()

        if len(emb_check.data) == 0:
            print(f"\n  📝 {law['name_ar']}")
            try:
                text = f"{law['name_ar']}\n\n{law.get('full_text_ar', '')}"

                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text[:8000]
                )
                embedding = response.data[0].embedding

                supabase.table('law_embeddings').insert({
                    'law_id': law['id'],
                    'text_chunk': law['name_ar'],
                    'embedding': embedding,
                    'chunk_index': 0
                }).execute()

                print(f"    ✅ Embedding added")
            except Exception as e:
                print(f"    ❌ Error: {e}")

            time.sleep(1)

    # Step 2: Add new laws with embeddings
    print("\n\n📚 Step 2: Adding new laws with embeddings...")

    added_count = 0

    for i, law in enumerate(NEW_LAWS, 1):
        print(f"\n  [{i}/{len(NEW_LAWS)}] {law['name_ar']}")

        try:
            # Check if law already exists
            existing = supabase.table('laws').select('id').eq('name_ar', law['name_ar']).execute()

            if len(existing.data) > 0:
                print(f"    ⏭️  Already exists")
                continue

            # Insert law
            law_result = supabase.table('laws').insert({
                'name_ar': law['name_ar'],
                'law_number': law['law_number'],
                'full_text_ar': law['full_text_ar'],
                'url': f"https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/{1000 + i}"
            }).execute()

            law_id = law_result.data[0]['id']
            print(f"    ✅ Law saved")

            # Generate embedding
            print(f"    🧠 Generating embedding...")
            text = f"{law['name_ar']}\n\n{law['full_text_ar']}"

            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            embedding = response.data[0].embedding

            # Save embedding
            supabase.table('law_embeddings').insert({
                'law_id': law_id,
                'text_chunk': law['name_ar'],
                'embedding': embedding,
                'chunk_index': 0
            }).execute()

            print(f"    ✅ Embedding saved")
            added_count += 1

            time.sleep(1)

        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Step 3: Verify final state
    print("\n\n" + "=" * 80)
    print("📊 Final Database State")
    print("=" * 80)

    all_laws = supabase.table('laws').select('name_ar').execute()
    all_embeddings = supabase.table('law_embeddings').select('id').execute()

    print(f"\n✅ Total Laws: {len(all_laws.data)}")
    print(f"✅ Total Embeddings: {len(all_embeddings.data)}")
    print(f"✅ New Laws Added: {added_count}")

    print("\n📋 Available Laws:")
    for law in all_laws.data:
        print(f"  • {law['name_ar']}")

    print("\n" + "=" * 80)
    print("🎉 Ready! Try asking questions now:")
    print("=" * 80)
    print("  • ما هي عقوبة السرقة في النظام السعودي؟")
    print("  • كم ساعة عمل في اليوم حسب نظام العمل؟")
    print("  • ما هي حقوق المستهلك؟")
    print("  • ما عقوبة الجرائم المعلوماتية؟")

if __name__ == '__main__':
    main()
