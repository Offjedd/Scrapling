#!/usr/bin/env python3
"""Quick script to add laws via SQL"""

import time
from openai import OpenAI

def load_env():
    env = {}
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                env[key] = val
    return env

NEW_LAWS = [
    ("نظام الشركات", "M/132", "نظام الشركات: يجوز تأسيس أي من أنواع الشركات من قبل شخص أو أكثر. الشركة ذات المسؤولية المحدودة يجب أن يكون رأس مالها مقسماً إلى حصص متساوية القيمة."),
    ("نظام الجرائم المعلوماتية", "M/17", "نظام مكافحة الجرائم المعلوماتية: يعاقب بالسجن مدة لا تزيد على سنة وبغرامة 500,000 ريال كل من يدخل بشكل غير مشروع لإلغاء أو حذف بيانات خاصة."),
    ("نظام المرور", "M/85", "نظام المرور: لا يجوز قيادة مركبة آلية إلا بعد الحصول على رخصة قيادة. يجب التقيد بالسرعة المحددة. عقوبة القيادة تحت تأثير المسكرات: السجن شهر إلى سنة."),
    ("نظام حماية المستهلك", "M/24", "نظام حماية المستهلك: للمستهلك حق الحصول على معلومات واضحة. يحق استرجاع المنتج خلال 7 أيام في حال وجود عيب. يحظر الإعلان المضلل."),
    ("نظام الإجراءات الجزائية", "M/2", "نظام الإجراءات الجزائية: لا يجوز القبض أو التوقيف إلا في الأحوال المنصوص عليها. المتهم بريء حتى تثبت إدانته. للمتهم الحق في الاستعانة بمحام."),
    ("نظام الضمان الاجتماعي", "M/32", "نظام الضمان الاجتماعي: يهدف لتوفير الحماية للأسر الأشد حاجة. يشمل تكاليف المعيشة والصحة والتعليم. يشترط أن يكون المستفيد سعودياً مقيماً بالمملكة.")
]

def main():
    env = load_env()
    openai_client = OpenAI(api_key=env['OPENAI_API_KEY'])

    print("=" * 80)
    print("📚 Generating Embeddings for New Laws")
    print("=" * 80)

    for i, (name, number, text) in enumerate(NEW_LAWS, 1):
        print(f"\n[{i}/{len(NEW_LAWS)}] {name}")
        print(f"  🧠 Generating embedding...")

        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=f"{name}\n\n{text}"
            )
            embedding = response.data[0].embedding

            # Write to file
            filename = f"law_{i}_embedding.sql"
            with open(filename, 'w') as f:
                f.write(f"-- {name}\n")
                f.write(f"-- Insert law and embedding\n\n")
                f.write(f"WITH new_law AS (\n")
                f.write(f"  INSERT INTO laws (name_ar, law_number, full_text_ar, url)\n")
                f.write(f"  VALUES (\n")
                f.write(f"    '{name}',\n")
                f.write(f"    '{number}',\n")
                f.write(f"    '{text}',\n")
                f.write(f"    'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/{1000+i}'\n")
                f.write(f"  )\n")
                f.write(f"  ON CONFLICT (url) DO NOTHING\n")
                f.write(f"  RETURNING id\n")
                f.write(f")\n")
                f.write(f"INSERT INTO law_embeddings (law_id, text_chunk, embedding, chunk_index)\n")
                f.write(f"SELECT id, '{name}', '{embedding}'::vector, 0\n")
                f.write(f"FROM new_law;\n")

            print(f"  ✅ SQL file created: {filename}")
            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ SQL files generated!")
    print("=" * 80)
    print("\nSQL files created - execute them manually or via Supabase MCP")

if __name__ == '__main__':
    main()
