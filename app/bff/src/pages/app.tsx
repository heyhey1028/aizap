import { Hono } from 'hono';
import { Top } from './top';

const web = new Hono();

web.get('/top', (c) => {
  return c.html(<Top />);
});

export default web;
