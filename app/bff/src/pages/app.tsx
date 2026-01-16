import { Hono } from 'hono';
import { Top } from './top.js';

const web: Hono = new Hono();

web.get('/top', (c) => {
  return c.html(<Top />);
});

export default web;
