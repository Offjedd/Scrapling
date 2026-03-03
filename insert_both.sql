-- Combined insertion of all 6 laws
-- Execute this in Supabase SQL Editor

-- نظام الشركات
DO $$
DECLARE
  v_law_id uuid;
BEGIN
  INSERT INTO laws (name_ar, law_number, full_text_ar, url)
  VALUES (
    'نظام الشركات',
    'M/132',
    'نظام الشركات: يجوز تأسيس أي من أنواع الشركات من قبل شخص أو أكثر. الشركة ذات المسؤولية المحدودة يجب أن يكون رأس مالها مقسماً إلى حصص متساوية القيمة.',
    'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1001'
  )
  ON CONFLICT (url) DO UPDATE SET name_ar = EXCLUDED.name_ar
  RETURNING id INTO v_law_id;

  RAISE NOTICE 'Inserted law: %', v_law_id;
END $$;

-- نظام الجرائم المعلوماتية
INSERT INTO laws (name_ar, law_number, full_text_ar, url)
VALUES (
  'نظام الجرائم المعلوماتية',
  'M/17',
  'نظام مكافحة الجرائم المعلوماتية: يعاقب بالسجن مدة لا تزيد على سنة وبغرامة 500,000 ريال كل من يدخل بشكل غير مشروع لإلغاء أو حذف بيانات خاصة.',
  'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1002'
)
ON CONFLICT (url) DO NOTHING;

-- نظام المرور
INSERT INTO laws (name_ar, law_number, full_text_ar, url)
VALUES (
  'نظام المرور',
  'M/85',
  'نظام المرور: لا يجوز قيادة مركبة آلية إلا بعد الحصول على رخصة قيادة. يجب التقيد بالسرعة المحددة. عقوبة القيادة تحت تأثير المسكرات: السجن شهر إلى سنة.',
  'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1003'
)
ON CONFLICT (url) DO NOTHING;

-- نظام حماية المستهلك
INSERT INTO laws (name_ar, law_number, full_text_ar, url)
VALUES (
  'نظام حماية المستهلك',
  'M/24',
  'نظام حماية المستهلك: للمستهلك حق الحصول على معلومات واضحة. يحق استرجاع المنتج خلال 7 أيام في حال وجود عيب. يحظر الإعلان المضلل.',
  'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1004'
)
ON CONFLICT (url) DO NOTHING;

-- نظام الإجراءات الجزائية
INSERT INTO laws (name_ar, law_number, full_text_ar, url)
VALUES (
  'نظام الإجراءات الجزائية',
  'M/2',
  'نظام الإجراءات الجزائية: لا يجوز القبض أو التوقيف إلا في الأحوال المنصوص عليها. المتهم بريء حتى تثبت إدانته. للمتهم الحق في الاستعانة بمحام.',
  'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1005'
)
ON CONFLICT (url) DO NOTHING;

-- نظام الضمان الاجتماعي
INSERT INTO laws (name_ar, law_number, full_text_ar, url)
VALUES (
  'نظام الضمان الاجتماعي',
  'M/32',
  'نظام الضمان الاجتماعي: يهدف لتوفير الحماية للأسر الأشد حاجة. يشمل تكاليف المعيشة والصحة والتعليم. يشترط أن يكون المستفيد سعودياً مقيماً بالمملكة.',
  'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/1006'
)
ON CONFLICT (url) DO NOTHING;
