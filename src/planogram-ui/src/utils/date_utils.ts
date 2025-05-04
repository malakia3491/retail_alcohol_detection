export const formatDate = (d: string | Date | null | undefined) => {
    if (d == null) {
      return '—';
    }

    let dt: Date;
    if (typeof d === 'string') {
      const isoMatch = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(d);
      const isoString = isoMatch ? `${d}Z` : d;
      dt = new Date(isoString);
    } else {
      dt = d;
    }

    if (isNaN(dt.getTime())) {
      console.warn('Invalid date passed to formatDate:', d);
      return '—';
    }

    return dt.toLocaleDateString('ru-RU', {
      year:   'numeric',
      month:  'long',
      day:    'numeric',
    });
  };