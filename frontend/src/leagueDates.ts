const BUNDESLIGA_SEASON_DATES_DICT: Record<string, [number[], number[]]> = {
  //yy, mm, dd
  2020: [
    [2020, 7, 18],
    [2021, 6, 22],
  ],
  2021: [
    [2021, 7, 13],
    [2022, 6, 14],
  ],
  2024: [
    [2024, 7, 23],
    [2025, 6, 17],
  ],
  2023: [
    [2023, 7, 18],
    [2024, 6, 18],
  ],
  2022: [
    [2022, 7, 5],
    [2023, 6, 27],
  ],
  2025: [
    [2025, 7, 22],
    [2026, 6, 16],
  ],
};

const LALIGA_SEASON_DATES_DICT = {
  2020: [
    [2020, 9, 12],
    [2021, 5, 23],
  ],
  2021: [
    [2021, 8, 13],
    [2022, 5, 22],
  ],
  2022: [
    [2022, 8, 12],
    [2023, 6, 4],
  ],
  2023: [
    [2023, 8, 11],
    [2024, 5, 26],
  ],
  2024: [
    [2024, 8, 15],
    [2025, 5, 25],
  ],
};

const SERIEA_DATES_DICT = {
  2020: [
    [2020, 9, 19],
    [2021, 5, 23],
  ],
  2021: [
    [2021, 8, 13],
    [2022, 5, 22],
  ],
  2022: [
    [2022, 8, 12],
    [2023, 6, 4],
  ],
  2023: [
    [2023, 8, 11],
    [2024, 5, 26],
  ],
  2024: [
    [2024, 8, 15],
    [2025, 5, 25],
  ],
  2025: [
    [2025, 8, 20],
    [2026, 5, 30],
  ],
};

const SEASON_DATES_DICT: Record<string, [number[], number[]]> =
  BUNDESLIGA_SEASON_DATES_DICT;

export function convertDateStrToSeason(
  dateStr: string,
  seasonDatesDict: Record<string, [number[], number[]]> = SEASON_DATES_DICT
): number {
  const dateYear = Number(dateStr.substring(0, 4));
  const dateMonth = Number(dateStr.substring(5, 7));
  const dateDay = Number(dateStr.substring(8, 10));

  for (const key of Object.keys(seasonDatesDict)) {
    const [start, end] = seasonDatesDict[key];
    const [startYear, startMonth, startDay] = start;
    const [endYear, endMonth, endDay] = end;

    // Before start year
    if (dateYear < startYear) continue;

    // Same start year
    if (dateYear === startYear) {
      if (dateMonth > startMonth) return Number(key);
      if (dateMonth === startMonth && dateDay >= startDay) return Number(key);
    }

    // After end year → skip
    if (dateYear > endYear) continue;

    // Same end year
    if (dateYear === endYear) {
      if (dateMonth < endMonth) return Number(key);
      if (dateMonth === endMonth && dateDay <= endDay) return Number(key);
    }
  }

  console.error(
    `Error: ${dateYear}/${dateMonth}/${dateDay} not in SEASON_DATES_DICT`
  );
  return dateYear;
}
